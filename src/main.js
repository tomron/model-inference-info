/**
 * Main application entry point.
 * Coordinates data loading, filtering, sorting, and rendering.
 */

import { loadPricingData, getAllModels, getLastUpdated, formatTimestamp } from './data.js';
import { renderTable } from './table.js';
import { initSorting, sortModels } from './sort.js';
import { initFilters, filterModels } from './filters.js';
import { formatRelativeTime } from './utils.js';

let allModels = [];
let filteredModels = [];
let sortedModels = [];

/**
 * Initialize the application.
 */
async function init() {
  try {
    // Load pricing data
    await loadPricingData();

    // Get all models
    allModels = getAllModels();

    // Initialize UI components
    initFilters();
    initSorting();

    // Set up event listeners
    setupEventListeners();

    // Update last updated timestamp
    updateLastUpdatedDisplay();

    // Initial render
    updateDisplay();
  } catch (error) {
    console.error('Failed to initialize application:', error);
    showError('Failed to load pricing data. Please try refreshing the page.');
  }
}

/**
 * Set up global event listeners.
 */
function setupEventListeners() {
  // Listen for filter changes
  document.addEventListener('filterChange', () => {
    updateDisplay();
  });

  // Listen for sort changes
  document.addEventListener('sortChange', (e) => {
    const { column, direction } = e.detail;
    sortedModels = sortModels(filteredModels, column, direction);
    renderTable(sortedModels);
  });
}

/**
 * Update the display based on current filters and sort.
 */
function updateDisplay() {
  // Apply filters
  filteredModels = filterModels(allModels);

  // Apply current sort if any
  const sortEvent = new CustomEvent('sortChange', {
    detail: { column: null, direction: 'asc' },
  });

  // Check if there's an active sort
  const currentSortColumn = document.querySelector('.sort-arrow.asc, .sort-arrow.desc');
  if (currentSortColumn) {
    const th = currentSortColumn.closest('th');
    const column = th.dataset.sort;
    const direction = currentSortColumn.classList.contains('asc') ? 'asc' : 'desc';
    sortedModels = sortModels(filteredModels, column, direction);
  } else {
    sortedModels = filteredModels;
  }

  // Render
  renderTable(sortedModels);
}

/**
 * Update the last updated timestamp display.
 */
function updateLastUpdatedDisplay() {
  const lastUpdated = getLastUpdated();
  const element = document.getElementById('lastUpdated');

  if (element && lastUpdated) {
    const formatted = formatTimestamp(lastUpdated);
    const relative = formatRelativeTime(lastUpdated);
    element.textContent = `Last updated: ${formatted} (${relative})`;
  }
}

/**
 * Show an error message to the user.
 * @param {string} message - Error message
 */
function showError(message) {
  const tbody = document.getElementById('tableBody');
  // Clear existing content safely
  while (tbody.firstChild) {
    tbody.removeChild(tbody.firstChild);
  }

  const row = document.createElement('tr');
  const cell = document.createElement('td');
  cell.colSpan = 5;
  cell.className = 'loading';
  cell.style.color = 'var(--danger)';
  cell.textContent = message;
  row.appendChild(cell);
  tbody.appendChild(row);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
