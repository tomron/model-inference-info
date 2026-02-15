/**
 * Utility functions for data formatting and analysis.
 */

/**
 * Format cost for display with currency symbol.
 * @param {number} cost - Cost value
 * @param {string} currency - Currency code (e.g., 'USD')
 * @param {string} unit - Pricing unit (e.g., 'per 1K tokens')
 * @returns {string} Formatted cost string
 */
export function formatCost(cost, currency = 'USD', unit = '') {
  const currencySymbol = getCurrencySymbol(currency);

  // Handle subscription pricing (cost is 0 with notes)
  if (cost === 0) {
    return 'See notes';
  }

  // Format with appropriate decimal places
  const formatted = cost < 0.001 ? cost.toFixed(6) : cost.toFixed(3);

  return `${currencySymbol}${formatted}`;
}

/**
 * Get currency symbol from currency code.
 * @param {string} currency - Currency code
 * @returns {string} Currency symbol
 */
function getCurrencySymbol(currency) {
  const symbols = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
  };
  return symbols[currency] || currency + ' ';
}

/**
 * Determine cost level (low/medium/high) for styling.
 * @param {number} cost - Cost value
 * @param {string} type - 'input' or 'output'
 * @returns {string} Cost level: 'low', 'medium', or 'high'
 */
export function getCostLevel(cost, type = 'input') {
  // Handle special case of $0 (subscription models)
  if (cost === 0) {
    return 'medium';
  }

  // Thresholds for input tokens
  if (type === 'input') {
    if (cost < 0.001) return 'low';
    if (cost < 0.005) return 'medium';
    return 'high';
  }

  // Thresholds for output tokens
  if (cost < 0.005) return 'low';
  if (cost < 0.020) return 'medium';
  return 'high';
}

/**
 * Find the lowest input and output costs across all models.
 * @param {Array} models - Array of model objects
 * @returns {Object} Object with 'input' and 'output' lowest costs
 */
export function findLowestCosts(models) {
  if (!models || models.length === 0) {
    return { input: null, output: null };
  }

  // Filter out $0 costs (subscription models)
  const validModels = models.filter(m =>
    m.pricing.inputTokens > 0 && m.pricing.outputTokens > 0
  );

  if (validModels.length === 0) {
    return { input: null, output: null };
  }

  const inputCosts = validModels.map(m => m.pricing.inputTokens);
  const outputCosts = validModels.map(m => m.pricing.outputTokens);

  return {
    input: Math.min(...inputCosts),
    output: Math.min(...outputCosts),
  };
}

/**
 * Format relative time (e.g., "2 hours ago").
 * @param {string} timestamp - ISO 8601 timestamp
 * @returns {string} Relative time string
 */
export function formatRelativeTime(timestamp) {
  if (!timestamp) return 'Unknown';

  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return timestamp;
  }
}
