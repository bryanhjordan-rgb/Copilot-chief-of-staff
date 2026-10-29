// Minimal ExcelScript type stubs so the Office Scripts in this folder
// type-check with tsc outside Excel (used by m365/tests).
declare namespace ExcelScript {
  interface Range {
    getValues(): (string | number | boolean)[][];
  }
  interface Table {
    getRange(): Range;
  }
  interface Workbook {
    getTable(name: string): Table | undefined;
  }
}
