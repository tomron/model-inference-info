/**
 * Filtering functionality for the pricing table.
 */

import { getProviders, getRegions } from './data.js';

let currentFilters = {
  provider: '',
  region: '',
  search: '',
};

/**
 * Initialize filter controls.
 */
export function initFilters() {
  populateProviderFilter();
  populateRegionFilter();
  attachFilterListeners();
}

/**
 * Populate the provider filter dropdown.
 */
function populateProviderFilter() {
  const select = document.getElementById('providerFilter');
  const providers = getProviders();

  // Clear existing options except the first (All Providers)
  while (select.options.length > 1) {
    select.remove(1);
  }

  // Add provider options
  providers.forEach(provider => {
    const option = document.createElement('option');
    option.value = provider;
    option.textContent = provider;
    select.appendChild(option);
  });
}

/**
 * Populate the region filter dropdown.
 */
function populateRegionFilter() {
  const select = document.getElementById('regionFilter');
  const regions = getRegions();

  // Clear existing options except the first (All Regions)
  while (select.options.length > 1) {
    select.remove(1);
  }

  // Add region options
  regions.forEach(region => {
    const option = document.createElement('option');
    option.value = region;
    option.textContent = region;
    select.appendChild(option);
  });
}

/**
 * Attach event listeners to filter controls.
 */
function attachFilterListeners() {
  const providerFilter = document.getElementById('providerFilter');
  const regionFilter = document.getElementById('regionFilter');
  const searchBox = document.getElementById('searchBox');
  const clearButton = document.getElementById('clearFilters');

  providerFilter.addEventListener('change', (e) => {
    currentFilters.provider = e.target.value;
    emitFilterChange();
  });

  regionFilter.addEventListener('change', (e) => {
    currentFilters.region = e.target.value;
    emitFilterChange();
  });

  searchBox.addEventListener('input', (e) => {
    currentFilters.search = e.target.value;
    emitFilterChange();
  });

  clearButton.addEventListener('click', () => {
    clearAllFilters();
  });
}

/**
 * Clear all filters and reset to default state.
 */
function clearAllFilters() {
  currentFilters = {
    provider: '',
    region: '',
    search: '',
  };

  // Reset UI
  document.getElementById('providerFilter').value = '';
  document.getElementById('regionFilter').value = '';
  document.getElementById('searchBox').value = '';

  emitFilterChange();
}

/**
 * Emit a filter change event.
 */
function emitFilterChange() {
  const event = new CustomEvent('filterChange', {
    detail: { ...currentFilters },
  });
  document.dispatchEvent(event);
}

/**
 * Apply filters to a list of models.
 * @param {Array} models - Array of model objects
 * @returns {Array} Filtered array of models
 */
export function filterModels(models) {
  if (!models) {
    return [];
  }

  let filtered = models;

  // Provider filter
  if (currentFilters.provider) {
    filtered = filtered.filter(model =>
      model.provider === currentFilters.provider
    );
  }

  // Region filter
  if (currentFilters.region) {
    filtered = filtered.filter(model =>
      model.regions && model.regions.includes(currentFilters.region)
    );
  }

  // Search filter (searches in provider name and model name)
  if (currentFilters.search) {
    const searchLower = currentFilters.search.toLowerCase();
    filtered = filtered.filter(model =>
      model.provider.toLowerCase().includes(searchLower) ||
      model.name.toLowerCase().includes(searchLower) ||
      model.modelId.toLowerCase().includes(searchLower)
    );
  }

  return filtered;
}

/**
 * Get current filter state.
 * @returns {Object} Current filters
 */
export function getCurrentFilters() {
  return { ...currentFilters };
}
