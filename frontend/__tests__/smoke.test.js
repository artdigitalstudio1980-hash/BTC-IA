describe("frontend smoke", () => {
  test("package.json has next", () => {
    const pkg = require("../package.json");
    expect(pkg.dependencies.next).toBeDefined();
    expect(pkg.dependencies.react).toBeDefined();
  });
  test("env example has required vars", () => {
    const fs = require("fs");
    const txt = fs.readFileSync("../.env.example", "utf8");
    expect(txt).toMatch(/APP_MODE/);
    expect(txt).toMatch(/LIVE_TRADING=false/);
  });
});
