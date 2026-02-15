/**
 * Table rendering module.
 * Handles rendering the pricing table with data.
 */

import { formatCost, getCostLevel, findLowestCosts } from './utils.js';

let expandedRows = new Set();

/**
 * Get a unique row identifier for a model.
 * @param {Object} model - Model data
 * @returns {string} Unique identifier
 */
function getRowId(model) {
  return `${model.provider}:${model.modelId}`;
}

/**
 * Render the pricing table with model data.
 * @param {Array} models - Array of model objects
 */
export function renderTable(models) {
  const tbody = document.getElementById('tableBody');

  if (!models || models.length === 0) {
    tbody.innerHTML = '';
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 5;
    cell.className = 'loading';
    cell.textContent = 'No models found matching your filters.';
    row.appendChild(cell);
    tbody.appendChild(row);
    return;
  }

  // Find lowest costs for highlighting
  const lowestCosts = findLowestCosts(models);

  // Clear existing rows
  tbody.innerHTML = '';

  // Render each model
  models.forEach(model => {
    const row = createModelRow(model, lowestCosts);
    tbody.appendChild(row);

    // Add expanded details row if this model was expanded
    const rowId = getRowId(model);
    if (expandedRows.has(rowId)) {
      const detailsRow = createDetailsRow(model);
      tbody.appendChild(detailsRow);
    }
  });
}

/**
 * Create a table row for a model.
 * @param {Object} model - Model data
 * @param {Object} lowestCosts - Lowest cost information
 * @returns {HTMLElement} Table row element
 */
function createModelRow(model, lowestCosts) {
  const row = document.createElement('tr');
  const rowId = getRowId(model);
  row.dataset.rowId = rowId;
  row.style.cursor = 'pointer';
  row.addEventListener('click', () => toggleRowDetails(model));

  if (expandedRows.has(rowId)) {
    row.classList.add('expanded');
  }

  const inputCost = model.pricing.inputTokens;
  const outputCost = model.pricing.outputTokens;
  const inputLevel = getCostLevel(inputCost, 'input');
  const outputLevel = getCostLevel(outputCost, 'output');

  // Provider cell
  const providerCell = document.createElement('td');
  providerCell.dataset.label = 'Provider';
  const providerSpan = document.createElement('span');
  providerSpan.className = 'provider-name';
  providerSpan.textContent = model.provider;
  providerCell.appendChild(providerSpan);
  row.appendChild(providerCell);

  // Model cell
  const modelCell = document.createElement('td');
  modelCell.dataset.label = 'Model';
  const modelNameDiv = document.createElement('div');
  modelNameDiv.className = 'model-name';
  modelNameDiv.textContent = model.name;
  const modelIdDiv = document.createElement('div');
  modelIdDiv.className = 'model-id';
  modelIdDiv.textContent = model.modelId;
  modelCell.appendChild(modelNameDiv);
  modelCell.appendChild(modelIdDiv);
  row.appendChild(modelCell);

  // Input cost cell
  const inputCell = document.createElement('td');
  inputCell.dataset.label = 'Input Cost';
  inputCell.className = `cost cost-${inputLevel}`;
  inputCell.textContent = formatCost(inputCost, model.pricing.currency, model.pricing.unit);
  const isLowestInput = lowestCosts.input === inputCost;
  if (isLowestInput) {
    const badge = document.createElement('span');
    badge.className = 'badge badge-lowest';
    badge.textContent = 'Lowest';
    inputCell.appendChild(badge);
  }
  row.appendChild(inputCell);

  // Output cost cell
  const outputCell = document.createElement('td');
  outputCell.dataset.label = 'Output Cost';
  outputCell.className = `cost cost-${outputLevel}`;
  outputCell.textContent = formatCost(outputCost, model.pricing.currency, model.pricing.unit);
  const isLowestOutput = lowestCosts.output === outputCost;
  if (isLowestOutput) {
    const badge = document.createElement('span');
    badge.className = 'badge badge-lowest';
    badge.textContent = 'Lowest';
    outputCell.appendChild(badge);
  }
  row.appendChild(outputCell);

  // Regions cell
  const regionsCell = document.createElement('td');
  regionsCell.dataset.label = 'Regions';
  regionsCell.className = 'regions';
  if (model.regions && model.regions.length > 0) {
    model.regions.forEach(region => {
      const tag = document.createElement('span');
      tag.className = 'region-tag';
      tag.textContent = region;
      regionsCell.appendChild(tag);
      regionsCell.appendChild(document.createTextNode(' '));
    });
  } else {
    const naSpan = document.createElement('span');
    naSpan.style.color = 'var(--text-secondary)';
    naSpan.textContent = 'N/A';
    regionsCell.appendChild(naSpan);
  }
  row.appendChild(regionsCell);

  return row;
}

/**
 * Create expanded details row for a model.
 * @param {Object} model - Model data
 * @returns {HTMLElement} Details row element
 */
function createDetailsRow(model) {
  const row = document.createElement('tr');
  row.className = 'expanded-details';
  const rowId = getRowId(model);
  row.dataset.detailsFor = rowId;

  const cell = document.createElement('td');
  cell.colSpan = 5;

  const detailRow = document.createElement('div');
  detailRow.className = 'detail-row';

  // Model ID
  const modelIdItem = createDetailItem('Model ID', model.modelId);
  detailRow.appendChild(modelIdItem);

  // Unit
  const unitItem = createDetailItem('Unit', model.pricing.unit);
  detailRow.appendChild(unitItem);

  // Currency
  const currencyItem = createDetailItem('Currency', model.pricing.currency);
  detailRow.appendChild(currencyItem);

  // Notes (if present)
  if (model.notes) {
    const notesItem = createDetailItem('Notes', model.notes);
    detailRow.appendChild(notesItem);
  }

  // All regions (if present)
  if (model.regions && model.regions.length > 0) {
    const regionsItem = createDetailItem(
      `All Regions (${model.regions.length})`,
      model.regions.join(', ')
    );
    detailRow.appendChild(regionsItem);
  }

  cell.appendChild(detailRow);
  row.appendChild(cell);
  return row;
}

/**
 * Create a detail item element.
 * @param {string} label - Detail label
 * @param {string} value - Detail value
 * @returns {HTMLElement} Detail item element
 */
function createDetailItem(label, value) {
  const item = document.createElement('div');
  item.className = 'detail-item';

  const labelDiv = document.createElement('div');
  labelDiv.className = 'detail-label';
  labelDiv.textContent = label;

  const valueDiv = document.createElement('div');
  valueDiv.className = 'detail-value';
  valueDiv.textContent = value;

  item.appendChild(labelDiv);
  item.appendChild(valueDiv);

  return item;
}

/**
 * Toggle expanded details for a model row.
 * @param {Object} model - Model data
 */
function toggleRowDetails(model) {
  const rowId = getRowId(model);

  if (expandedRows.has(rowId)) {
    expandedRows.delete(rowId);
    // Remove details row
    const detailsRow = document.querySelector(`tr[data-details-for="${CSS.escape(rowId)}"]`);
    if (detailsRow) {
      detailsRow.remove();
    }
    // Remove expanded class
    const mainRow = document.querySelector(`tr[data-row-id="${CSS.escape(rowId)}"]`);
    if (mainRow) {
      mainRow.classList.remove('expanded');
    }
  } else {
    expandedRows.add(rowId);
    // Add details row
    const mainRow = document.querySelector(`tr[data-row-id="${CSS.escape(rowId)}"]`);
    if (mainRow) {
      mainRow.classList.add('expanded');
      const detailsRow = createDetailsRow(model);
      mainRow.after(detailsRow);
    }
  }
}
