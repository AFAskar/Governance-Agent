import { defineConfig } from "eslint/config";

import { baseConfig } from "@governance/eslint-config/base";
import { reactConfig } from "@governance/eslint-config/react";

export default defineConfig(
  {
    ignores: ["dist/**"],
  },
  baseConfig,
  reactConfig,
);
