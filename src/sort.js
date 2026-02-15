/**
 * Sorting functionality for the pricing table.
 */

let currentSort = {
  column: null,
  direction: 'asc', // 'asc' or 'desc'
};

/**
 * Initialize sorting event listeners on table headers.
 */
export function initSorting() {
  const headers = document.querySelectorAll('th[data-sort]');

  headers.forEach(header => {
    header.addEventListener('click', () => {
      const column = header.dataset.sort;
      handleSort(column);
    });
  });
}

/**
 * Handle sorting when a column header is clicked.
 * @param {string} column - Column identifier
 */
function handleSort(column) {
  // Toggle direction if clicking same column, otherwise default to asc
  if (currentSort.column === column) {
    currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
  } else {
    currentSort.column = column;
    currentSort.direction = 'asc';
  }

  // Update visual indicators
  updateSortArrows();

  // Trigger sort (this will be called from main.js)
  const event = new CustomEvent('sortChange', {
    detail: { column: currentSort.column, direction: currentSort.direction },
  });
  document.dispatchEvent(event);
}

/**
 * Update sort arrow indicators in table headers.
 */
function updateSortArrows() {
  // Clear all arrows
  document.querySelectorAll('.sort-arrow').forEach(arrow => {
    arrow.classList.remove('asc', 'desc');
  });

  // Set arrow for current sort column
  if (currentSort.column) {
    const header = document.querySelector(`th[data-sort="${currentSort.column}"]`);
    if (header) {
      const arrow = header.querySelector('.sort-arrow');
      if (arrow) {
        arrow.classList.add(currentSort.direction);
      }
    }
  }
}

/**
 * Sort an array of models by the given column and direction.
 * @param {Array} models - Array of model objects
 * @param {string} column - Column to sort by
 * @param {string} direction - 'asc' or 'desc'
 * @returns {Array} Sorted array of models
 */
export function sortModels(models, column, direction) {
  if (!models || !column) {
    return models;
  }

  const sorted = [...models];

  sorted.sort((a, b) => {
    let aVal, bVal;

    switch (column) {
      case 'provider':
        aVal = a.provider.toLowerCase();
        bVal = b.provider.toLowerCase();
        break;

      case 'model':
        aVal = a.name.toLowerCase();
        bVal = b.name.toLowerCase();
        break;

      case 'input':
        aVal = a.pricing.inputTokens;
        bVal = b.pricing.inputTokens;
        break;

      case 'output':
        aVal = a.pricing.outputTokens;
        bVal = b.pricing.outputTokens;
        break;

      case 'regions':
        // Sort by number of regions, then by first region name
        aVal = a.regions ? a.regions.length : 0;
        bVal = b.regions ? b.regions.length : 0;
        if (aVal === bVal && a.regions && b.regions && a.regions.length > 0) {
          aVal = a.regions[0].toLowerCase();
          bVal = b.regions[0].toLowerCase();
        }
        break;

      default:
        return 0;
    }

    // Compare values
    let comparison = 0;
    if (aVal < bVal) {
      comparison = -1;
    } else if (aVal > bVal) {
      comparison = 1;
    }

    // Apply direction
    return direction === 'asc' ? comparison : -comparison;
  });

  return sorted;
}

/**
 * Get current sort state.
 * @returns {Object} Current sort state
 */
export function getCurrentSort() {
  return { ...currentSort };
}
