
import { createClient, createConfig } from "../ai-client/client";
import type { ClientOptions } from "../ai-client/types.gen";

export const getAIClient = () => {
    const baseUrl = process.env.AI_SERVICE_URL || "http://localhost:8000";
    const apiKey = process.env.AI_SERVICE_KEY;

    return createClient(
        createConfig<ClientOptions>({
            baseUrl,
            headers: apiKey
                ? {
                    Authorization: apiKey,
                }
                : undefined,
        })
    );
};
