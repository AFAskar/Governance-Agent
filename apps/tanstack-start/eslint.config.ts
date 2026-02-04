import { defineConfig } from "eslint/config";

import { baseConfig, restrictEnvAccess } from "@governance/eslint-config/base";
import { reactConfig } from "@governance/eslint-config/react";

export default defineConfig(
  {
    ignores: [".nitro/**", ".output/**", ".tanstack/**"],
  },
  baseConfig,
  reactConfig,
  restrictEnvAccess,
);
