import { useState, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "@tanstack/react-form";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { NDI_DOMAINS } from "~/lib/ndi-domains";
import { Button } from "@governance/ui/button";
import { Input } from "@governance/ui/input";
import {
    Field,
    FieldContent,
    FieldError,
    FieldGroup,
    FieldLabel,
} from "@governance/ui/field";
import { toast } from "@governance/ui/toast";
import { useTRPC } from "~/lib/trpc";

const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            // remove data:application/pdf;base64, prefix
            const result = reader.result as string;
            const base64 = result.split(',')[1];
            if (base64) resolve(base64);
            else reject(new Error('Failed to convert file to base64'));
        };
        reader.onerror = error => reject(error);
    });
};

export const Route = createFileRoute("/submit")({
    component: RouteComponent,
});

interface FileWithDomain {
    file: File;
    domainId: string;
}

function RouteComponent() {
    const navigate = useNavigate();
    const [filesByDomain, setFilesByDomain] = useState<Record<string, File[]>>({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const trpc = useTRPC();
    const createSubmission = useMutation(trpc.submission.create.mutationOptions());

    const form = useForm({
        defaultValues: {
            companyName: "",
        },
        onSubmit: async ({ value }) => {
            // Validate company name
            if (!value.companyName.trim()) {
                toast.error("Please enter your company name");
                return;
            }

            // Check if at least one file is uploaded
            const totalFiles = Object.values(filesByDomain).reduce(
                (sum, files) => sum + files.length,
                0
            );
            if (totalFiles === 0) {
                toast.error("Please upload at least one file");
                return;
            }

            setIsSubmitting(true);

            try {
                const filesToUpload = [];
                for (const [domainId, files] of Object.entries(filesByDomain)) {
                    const domain = NDI_DOMAINS.find(d => d.id === domainId);
                    const domainName = domain ? domain.name : "Unknown";
                    for (const file of files) {
                        const content = await fileToBase64(file);
                        filesToUpload.push({
                            name: file.name,
                            content,
                            type: file.type,
                            domainId,
                            domainName,
                            size: file.size
                        });
                    }
                }

                const result = await createSubmission.mutateAsync({
                    companyName: value.companyName,
                    files: filesToUpload
                });

                if (result.evaluationFailed) {
                    toast.success("Submission saved. AI evaluation could not be completed — you can retry later.");
                } else {
                    toast.success("Submission created and evaluated successfully!");
                }
                await navigate({ to: "/admin/ndi" });
            } catch (error) {
                toast.error("Failed to save submission. Please try again.");
                console.error(error);
            } finally {
                setIsSubmitting(false);
            }
        },
    });

    const handleFileChange = useCallback(
        (domainId: string, files: FileList | null) => {
            if (!files) return;

            const fileArray = Array.from(files);
            const currentFiles = filesByDomain[domainId] || [];

            // Limit to 20 files per domain
            const newFiles = [...currentFiles, ...fileArray].slice(0, 20);

            setFilesByDomain((prev) => ({
                ...prev,
                [domainId]: newFiles,
            }));
        },
        [filesByDomain]
    );

    const removeFile = useCallback((domainId: string, index: number) => {
        setFilesByDomain((prev) => ({
            ...prev,
            [domainId]: (prev[domainId] || []).filter((_, i) => i !== index),
        }));
    }, []);

    return (
        <main className="container mx-auto px-4 py-12">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-ndmo-blue-dark mb-2">
                        NDI Assessment Submission
                    </h1>
                    <p className="text-ndmo-gray-medium">
                        Upload your documents for Nationality Data Index evaluation
                    </p>
                </div>

                {/* Form */}
                <form
                    onSubmit={(e) => {
                        e.preventDefault();
                        void form.handleSubmit();
                    }}
                    className="space-y-8"
                >
                    {/* Company Name */}
                    <div className="bg-white rounded-xl p-6 shadow-sm border">
                        <form.Field name="companyName">
                            {(field) => {
                                const isInvalid =
                                    field.state.meta.isTouched && !field.state.meta.isValid;
                                return (
                                    <Field data-invalid={isInvalid}>
                                        <FieldContent>
                                            <FieldLabel htmlFor={field.name}>
                                                Company Name *
                                            </FieldLabel>
                                        </FieldContent>
                                        <Input
                                            id={field.name}
                                            name={field.name}
                                            value={field.state.value}
                                            onBlur={field.handleBlur}
                                            onChange={(e) => field.handleChange(e.target.value)}
                                            aria-invalid={isInvalid}
                                            placeholder="Enter your company name"
                                            className="mt-2"
                                        />
                                        {isInvalid && <FieldError errors={field.state.meta.errors} />}
                                    </Field>
                                );
                            }}
                        </form.Field>
                    </div>

                    {/* Upload Documents Section */}
                    <div className="bg-white rounded-xl p-6 shadow-sm border">
                        <h2 className="text-2xl font-bold text-ndmo-blue-dark mb-6">
                            Upload Documents
                        </h2>

                        <div className="space-y-6">
                            {NDI_DOMAINS.map((domain) => (
                                <DomainUploadSection
                                    key={domain.id}
                                    domain={domain}
                                    files={filesByDomain[domain.id] || []}
                                    onFileChange={(files) => handleFileChange(domain.id, files)}
                                    onRemoveFile={(index) => removeFile(domain.id, index)}
                                />
                            ))}
                        </div>
                    </div>

                    {/* Submit Button */}
                    <div className="flex justify-end">
                        <Button
                            type="submit"
                            disabled={isSubmitting}
                            className="bg-ndmo-blue-medium hover:bg-ndmo-blue-dark text-primary px-8 py-3 text-lg font-semibold"
                        >
                            {isSubmitting ? "Submitting..." : "Submit for Assessment"}
                        </Button>
                    </div>
                </form>
            </div>
        </main>
    );
}

interface DomainUploadSectionProps {
    domain: (typeof NDI_DOMAINS)[number];
    files: File[];
    onFileChange: (files: FileList | null) => void;
    onRemoveFile: (index: number) => void;
}

function DomainUploadSection({
    domain,
    files,
    onFileChange,
    onRemoveFile,
}: DomainUploadSectionProps) {
    return (
        <div className="border-b border-ndmo-gray-light pb-6 last:border-b-0">
            <div className="flex items-start gap-4">
                {/* Domain Number */}
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-ndmo-blue-medium text-primary flex items-center justify-center font-bold text-sm">
                    {domain.order}
                </div>

                {/* Domain Content */}
                <div className="flex-1">
                    <h3 className="font-semibold text-ndmo-blue-dark mb-3">
                        {domain.name}
                    </h3>

                    {/* File Upload */}
                    <div className="space-y-3">
                        <label className="block">
                            <input
                                type="file"
                                multiple
                                accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.csv"
                                onChange={(e) => onFileChange(e.target.files)}
                                className="block w-full text-sm text-ndmo-gray-medium
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-lg file:border-0
                  file:text-sm file:font-semibold
                  file:bg-ndmo-blue-pale file:text-ndmo-blue-dark
                  hover:file:bg-ndmo-blue-light hover:file:text-primary
                  file:cursor-pointer file:transition-colors"
                            />
                        </label>

                        {/* File List */}
                        {files.length > 0 && (
                            <div className="space-y-2">
                                {files.map((file, index) => (
                                    <div
                                        key={index}
                                        className="flex items-center justify-between bg-ndmo-gray-light/50 rounded-lg px-3 py-2"
                                    >
                                        <div className="flex items-center gap-2 flex-1 min-w-0">
                                            <svg
                                                className="w-4 h-4 text-ndmo-blue-medium flex-shrink-0"
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth={2}
                                                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                                />
                                            </svg>
                                            <span className="text-sm text-ndmo-gray-dark truncate">
                                                {file.name}
                                            </span>
                                            <span className="text-xs text-ndmo-gray-medium flex-shrink-0">
                                                ({(file.size / 1024).toFixed(1)} KB)
                                            </span>
                                        </div>
                                        <button
                                            type="button"
                                            onClick={() => onRemoveFile(index)}
                                            className="ml-2 text-ndmo-red hover:text-red-700 flex-shrink-0"
                                        >
                                            <svg
                                                className="w-4 h-4"
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth={2}
                                                    d="M6 18L18 6M6 6l12 12"
                                                />
                                            </svg>
                                        </button>
                                    </div>
                                ))}
                                {files.length >= 20 && (
                                    <p className="text-xs text-ndmo-yellow">
                                        Maximum 20 files reached for this domain
                                    </p>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
