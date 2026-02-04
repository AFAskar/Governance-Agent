import { defineConfig } from "eslint/config";

import { baseConfig } from "@governance/eslint-config/base";

export default defineConfig(
  {
    ignores: ["dist/**"],
  },
  baseConfig,
);
