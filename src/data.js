/**
 * Data loading and management module.
 * Handles fetching and parsing pricing data from JSON.
 */

let pricingData = null;

/**
 * Load pricing data from JSON file.
 * @returns {Promise<Object>} The pricing data
 */
export async function loadPricingData() {
  try {
    const baseUrl = import.meta.env.BASE_URL;
    const response = await fetch(`${baseUrl}data/pricing.json`);
    if (!response.ok) {
      throw new Error(`Failed to load pricing data: ${response.status}`);
    }
    pricingData = await response.json();
    return pricingData;
  } catch (error) {
    console.error('Error loading pricing data:', error);
    throw error;
  }
}

/**
 * Get all models flattened into a single array.
 * @returns {Array} Array of model objects with provider info
 */
export function getAllModels() {
  if (!pricingData) {
    return [];
  }

  const models = [];
  for (const provider of pricingData.providers) {
    for (const model of provider.models) {
      models.push({
        provider: provider.name,
        providerLastUpdated: provider.lastUpdated,
        ...model,
      });
    }
  }
  return models;
}

/**
 * Get unique provider names.
 * @returns {Array<string>} Sorted array of provider names
 */
export function getProviders() {
  if (!pricingData) {
    return [];
  }
  return [...new Set(pricingData.providers.map(p => p.name))].sort();
}

/**
 * Get unique regions across all models.
 * @returns {Array<string>} Sorted array of region names
 */
export function getRegions() {
  if (!pricingData) {
    return [];
  }

  const regions = new Set();
  for (const provider of pricingData.providers) {
    for (const model of provider.models) {
      if (model.regions) {
        model.regions.forEach(region => regions.add(region));
      }
    }
  }
  return Array.from(regions).sort();
}

/**
 * Get the global last updated timestamp.
 * @returns {string|null} ISO 8601 timestamp or null
 */
export function getLastUpdated() {
  return pricingData ? pricingData.lastUpdated : null;
}

/**
 * Format timestamp for display.
 * @param {string} timestamp - ISO 8601 timestamp
 * @returns {string} Formatted date string
 */
export function formatTimestamp(timestamp) {
  if (!timestamp) return 'Unknown';

  try {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZoneName: 'short',
    });
  } catch (error) {
    console.error('Error formatting timestamp:', error);
    return timestamp;
  }
}

/**
 * Get cached pricing data.
 * @returns {Object|null} The pricing data or null if not loaded
 */
export function getPricingData() {
  return pricingData;
}
