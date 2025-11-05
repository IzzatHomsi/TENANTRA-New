import { build } from "vite";

async function main() {
  try {
    process.env.ANALYZE = "true";
    await build();
    console.log("Bundle analysis generated at dist/bundle-analysis.html");
  } catch (error) {
    console.error("Bundle analysis failed:", error);
    process.exit(1);
  }
}

main();
