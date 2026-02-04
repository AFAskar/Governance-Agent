/**
 * NDI Domains Configuration
 * 15 domains for Nationality Data Index assessment
 */

export const NDI_DOMAINS = [
  {
    id: "1_Data_Governance",
    name: "Data Governance",
    order: 1,
  },
  {
    id: "2_Data_Catalog_Metadata",
    name: "Data Catalog & Metadata",
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
    id: "5_Document_Management",
    name: "Document Management",
    order: 5,
  },
  {
    id: "6_Data_Architecture",
    name: "Data Architecture",
    order: 6,
  },
  {
    id: "7_Data_Sharing",
    name: "Data Sharing",
    order: 7,
  },
  {
    id: "8_Master_Data",
    name: "Master Data",
    order: 8,
  },
  {
    id: "9_Analytics_BI",
    name: "Analytics & BI",
    order: 9,
  },
  {
    id: "10_Data_Value",
    name: "Data Value",
    order: 10,
  },
  {
    id: "11_Open_Data",
    name: "Open Data",
    order: 11,
  },
  {
    id: "12_Freedom_of_Information",
    name: "Freedom of Information",
    order: 12,
  },
  {
    id: "13_Data_Classification",
    name: "Data Classification",
    order: 13,
  },
  {
    id: "14_Personal_Data_Protection",
    name: "Personal Data Protection",
    order: 14,
  },
  {
    id: "15_Data_Security",
    name: "Data Security",
    order: 15,
  },
] as const;

export type NDIDomainId = (typeof NDI_DOMAINS)[number]["id"];
export type NDIDomain = (typeof NDI_DOMAINS)[number];
