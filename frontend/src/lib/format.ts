const rp = new Intl.NumberFormat('id-ID', { maximumFractionDigits: 0 });

export function formatRupiah(value: number): string {
	return `Rp${rp.format(Math.round(value))}`;
}

export function formatCompact(value: number): string {
	const abs = Math.abs(value);
	if (abs >= 1_000_000_000) return `Rp${(value / 1_000_000_000).toFixed(1).replace('.0', '')}B`;
	if (abs >= 1_000_000) return `Rp${(value / 1_000_000).toFixed(1).replace('.0', '')}M`;
	if (abs >= 1_000) return `Rp${(value / 1_000).toFixed(0)}K`;
	return `Rp${value}`;
}

const MONTHS = [
	'January',
	'February',
	'March',
	'April',
	'May',
	'June',
	'July',
	'August',
	'September',
	'October',
	'November',
	'December'
];

const MONTHS_SHORT = MONTHS.map((m) => m.slice(0, 3));

export function monthName(month: number): string {
	return MONTHS[month - 1] ?? '';
}

export function monthShort(month: number): string {
	return MONTHS_SHORT[month - 1] ?? '';
}

export function formatDate(iso: string): string {
	const [y, m, d] = iso.split('-');
	return `${d} ${monthShort(Number(m))} ${y}`;
}

export function todayIso(): string {
	const d = new Date();
	const pad = (n: number) => String(n).padStart(2, '0');
	return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export function nowMonthYear(): { month: number; year: number } {
	const d = new Date();
	return { month: d.getMonth() + 1, year: d.getFullYear() };
}
