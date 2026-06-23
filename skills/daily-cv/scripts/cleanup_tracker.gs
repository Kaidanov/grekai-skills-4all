/**
 * cleanup_tracker.gs — Google Apps Script template for job tracker maintenance.
 *
 * Setup:
 *   1. Open your Google Sheet.
 *   2. Extensions -> Apps Script.
 *   3. Paste this file.
 *   4. Set SPREADSHEET_ID and sheet names below.
 *   5. Run cleanupAll().
 *
 * This template contains no private spreadsheet IDs.
 */

const SPREADSHEET_ID = '<YOUR_SPREADSHEET_ID>';
const MAIN_SHEET = 'Applications';
const ARCHIVE_NAME = 'Archive';

const ARCHIVE_STATUSES = ['closed', 'expired', 'rejected', 'archived'];
const DELETE_STATUSES = ['irrelevant', 'not_a_fit'];

const HEADER_COLOR = '#1B4F72';
const HEADER_FONT = '#FFFFFF';
const ALT_ROW_COLOR = '#EBF5FB';
const WHITE = '#FFFFFF';

const STATUS_COLORS = {
  found: { bg: '#FEF9E7', font: '#7D6608' },
  validated: { bg: '#D6EAF8', font: '#1A5276' },
  ready_to_apply: { bg: '#D5F5E3', font: '#1E8449' },
  applied: { bg: '#D6EAF8', font: '#1A5276' },
  interviewing: { bg: '#E8DAEF', font: '#6C3483' },
  offer: { bg: '#D5F5E3', font: '#1E8449' },
  rejected: { bg: '#F2F3F4', font: '#7F8C8D' },
  closed: { bg: '#F2F3F4', font: '#7F8C8D' },
  proactive_outreach_pending: { bg: '#FDEBD0', font: '#935116' },
};

function cleanupAll() {
  if (SPREADSHEET_ID === '<YOUR_SPREADSHEET_ID>') {
    throw new Error('Set SPREADSHEET_ID before running cleanupAll().');
  }

  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  ensureArchiveSheet(spreadsheet);
  fixDatesAndArchive(spreadsheet);
  beautifyAllSheets(spreadsheet);
  SpreadsheetApp.flush();
  Logger.log('Tracker cleanup complete');
}

function ensureArchiveSheet(spreadsheet) {
  if (!spreadsheet.getSheetByName(ARCHIVE_NAME)) {
    const archive = spreadsheet.insertSheet(ARCHIVE_NAME, 1);
    const headers = [
      'date_found',
      'company',
      'title',
      'location',
      'work_mode',
      'status',
      'canonical_job_url',
      'apply_url',
      'source',
      'evidence',
      'score',
      'output_folder',
      'notes',
    ];
    archive.getRange(1, 1, 1, headers.length).setValues([headers]);
    Logger.log('Created archive sheet');
  }
}

function fixDatesAndArchive(spreadsheet) {
  const main = spreadsheet.getSheetByName(MAIN_SHEET);
  if (!main) {
    Logger.log('Main sheet not found: ' + MAIN_SHEET);
    return;
  }

  const archive = spreadsheet.getSheetByName(ARCHIVE_NAME);
  const lastRow = main.getLastRow();
  const lastCol = main.getLastColumn();
  if (lastRow < 2) return;

  const header = main.getRange(1, 1, 1, lastCol).getValues()[0].map(String);
  const dateColumn = Math.max(header.indexOf('date_found') + 1, 1);
  const statusColumn = Math.max(header.indexOf('status') + 1, 6);
  const data = main.getRange(2, 1, lastRow - 1, lastCol).getValues();
  const rowsToDelete = [];

  for (let index = data.length - 1; index >= 0; index--) {
    const row = data[index];
    const status = String(row[statusColumn - 1] || '').trim().toLowerCase();
    const dateRaw = String(row[dateColumn - 1] || '').trim();

    const isoDate = convertToISO(dateRaw);
    if (isoDate !== dateRaw) {
      main.getRange(index + 2, dateColumn).setValue(isoDate);
    }

    if (ARCHIVE_STATUSES.some((value) => status.includes(value))) {
      archive.appendRow(row);
      rowsToDelete.push(index + 2);
    } else if (DELETE_STATUSES.some((value) => status.includes(value))) {
      rowsToDelete.push(index + 2);
    }
  }

  rowsToDelete.sort((left, right) => right - left);
  rowsToDelete.forEach((rowNumber) => main.deleteRow(rowNumber));

  const remainingRows = main.getLastRow();
  if (remainingRows > 2) {
    main.getRange(2, 1, remainingRows - 1, main.getLastColumn()).sort({ column: dateColumn, ascending: false });
  }

  Logger.log('Removed rows from main sheet: ' + rowsToDelete.length);
}

function beautifyAllSheets(spreadsheet) {
  spreadsheet.getSheets().forEach((sheet) => {
    if (!sheet.isSheetHidden()) {
      beautifySheet(sheet);
    }
  });
}

function beautifySheet(sheet) {
  const lastRow = Math.max(sheet.getLastRow(), 1);
  const lastCol = Math.max(sheet.getLastColumn(), 1);

  sheet.getRange(1, 1, 1, lastCol)
    .setBackground(HEADER_COLOR)
    .setFontColor(HEADER_FONT)
    .setFontWeight('bold')
    .setHorizontalAlignment('center');

  sheet.setFrozenRows(1);

  for (let row = 2; row <= lastRow; row++) {
    sheet.getRange(row, 1, 1, lastCol).setBackground(row % 2 === 0 ? ALT_ROW_COLOR : WHITE);
  }

  for (let col = 1; col <= lastCol; col++) {
    sheet.autoResizeColumn(col);
    if (sheet.getColumnWidth(col) > 300) sheet.setColumnWidth(col, 300);
  }

  applyStatusColors(sheet, lastRow);
}

function applyStatusColors(sheet, lastRow) {
  const lastCol = sheet.getLastColumn();
  const header = sheet.getRange(1, 1, 1, lastCol).getValues()[0].map(String);
  const statusColumn = header.indexOf('status') + 1;
  if (statusColumn < 1) return;

  for (let row = 2; row <= lastRow; row++) {
    const cell = sheet.getRange(row, statusColumn);
    const status = String(cell.getValue()).trim().toLowerCase();
    const colors = STATUS_COLORS[status];
    if (colors) {
      cell.setBackground(colors.bg).setFontColor(colors.font).setFontWeight('bold');
    }
  }
}

function convertToISO(raw) {
  if (!raw) return raw;
  const value = String(raw).trim();
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value;

  const slashMatch = value.match(/^(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})$/);
  if (!slashMatch) return raw;

  const day = Number(slashMatch[1]);
  const month = Number(slashMatch[2]);
  let year = Number(slashMatch[3]);
  if (year < 100) year += 2000;

  return year + '-' + String(month).padStart(2, '0') + '-' + String(day).padStart(2, '0');
}