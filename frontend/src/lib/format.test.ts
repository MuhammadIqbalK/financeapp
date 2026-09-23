import { describe, expect, it } from 'vitest';
import { formatCompact, formatDate, formatRupiah, monthName } from './format';

describe('formatRupiah', () => {
	it('formats with Indonesian thousand separators', () => {
		expect(formatRupiah(8500000)).toBe('Rp8.500.000');
		expect(formatRupiah(50000)).toBe('Rp50.000');
		expect(formatRupiah(0)).toBe('Rp0');
	});

	it('rounds fractions', () => {
		expect(formatRupiah(1234.6)).toBe('Rp1.235');
	});
});

describe('formatCompact', () => {
	it('compacts large values', () => {
		expect(formatCompact(12000000)).toBe('Rp12M');
		expect(formatCompact(3500000)).toBe('Rp3.5M');
		expect(formatCompact(500)).toBe('Rp500');
	});
});

describe('formatDate', () => {
	it('renders "23 Sep 2026"', () => {
		expect(formatDate('2026-09-23')).toBe('23 Sep 2026');
	});
});

describe('monthName', () => {
	it('returns full month names', () => {
		expect(monthName(9)).toBe('September');
		expect(monthName(1)).toBe('January');
	});
});
