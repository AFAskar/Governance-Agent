/**
 * NDI Domains Configuration
 * 15 domains for Nationality Data Index assessment
 */

export const NDI_DOMAINS = [
  {
    id: "DG",
    name: "Data Governance",
    order: 1,
  },
  {
    id: "DCM",
    name: "Data Catalog & Metadata",
    order: 2,
  },
  {
    id: "DQ",
    name: "Data Quality",
    order: 3,
  },
  {
    id: "DO",
    name: "Data Operations",
    order: 4,
  },
  {
    id: "DM",
    name: "Document Management",
    order: 5,
  },
  {
    id: "DA",
    name: "Data Architecture",
    order: 6,
  },
  {
    id: "DS",
    name: "Data Sharing",
    order: 7,
  },
  {
    id: "MD",
    name: "Master Data",
    order: 8,
  },
  {
    id: "ABI",
    name: "Analytics & BI",
    order: 9,
  },
  {
    id: "DV",
    name: "Data Value",
    order: 10,
  },
  {
    id: "OD",
    name: "Open Data",
    order: 11,
  },
  {
    id: "FOI",
    name: "Freedom of Information",
    order: 12,
  },
  {
    id: "DC",
    name: "Data Classification",
    order: 13,
  },
  {
    id: "PDP",
    name: "Personal Data Protection",
    order: 14,
  },
  {
    id: "DSec",
    name: "Data Security",
    order: 15,
  },
] as const;

export type NDIDomainId = (typeof NDI_DOMAINS)[number]["id"];
export type NDIDomain = (typeof NDI_DOMAINS)[number];
