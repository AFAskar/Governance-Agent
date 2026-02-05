/**
 * NDI Domains Configuration
 * 12 domains for Nationality Data Index assessment
 */

export const NDI_DOMAINS = [
  {
    id: "1_Data_Governance",
    name: "Data Governance",
    order: 1,
  },
  {
    id: "2_Data_Catalog",
    name: "Data Catalog",
    order: 2,
  },
  {
    id: "3_Data_Quality",
    name: "Data Quality",
    order: 3,
  },
  {
    id: "4_Data_Operations",
    name: "Data Operations",
    order: 4,
  },
  {
    id: "5_Data_Security",
    name: "Data Security",
    order: 5,
  },
  {
    id: "6_Personal_Data_Protection",
    name: "Personal Data Protection",
    order: 6,
  },
  {
    id: "7_Data_Classification",
    name: "Data Classification",
    order: 7,
  },
  {
    id: "8_Training_Awareness",
    name: "Training & Awareness",
    order: 8,
  },
  {
    id: "9_Audit_Compliance",
    name: "Audit & Compliance",
    order: 9,
  },
  {
    id: "10_Risk_Management",
    name: "Risk Management",
    order: 10,
  },
  {
    id: "11_Governance_Meetings",
    name: "Governance Meetings",
    order: 11,
  },
  {
    id: "12_Supporting_Documents",
    name: "Supporting Documents",
    order: 12,
  },
] as const;

export type NDIDomainId = (typeof NDI_DOMAINS)[number]["id"];
export type NDIDomain = (typeof NDI_DOMAINS)[number];
