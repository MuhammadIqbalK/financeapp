<script lang="ts">
	import { categoriesApi } from '$lib/api';
	import type { Category, TxType } from '$lib/types';
	import Modal from '$lib/components/Modal.svelte';

	let items = $state<Category[]>([]);
	let error = $state('');
	let showForm = $state(false);
	let editing = $state<Category | null>(null);
	let deleting = $state<Category | null>(null);

	let name = $state('');
	let type = $state<TxType>('expense');

	const income = $derived(items.filter((c) => c.type === 'income'));
	const expense = $derived(items.filter((c) => c.type === 'expense'));

	async function load() {
		error = '';
		try {
			items = await categoriesApi.list();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load';
		}
	}

	$effect(() => {
		void load();
	});

	function openCreate(t: TxType) {
		editing = null;
		name = '';
		type = t;
		showForm = true;
	}

	function openEdit(c: Category) {
		editing = c;
		name = c.name;
		type = c.type;
		showForm = true;
	}

	async function save() {
		error = '';
		if (!name.trim()) return;
		try {
			if (editing) {
				await categoriesApi.update(editing.id, { name: name.trim(), type });
			} else {
				await categoriesApi.create({ name: name.trim(), type });
			}
			showForm = false;
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save';
		}
	}

	async function confirmDelete() {
		if (!deleting) return;
		try {
			await categoriesApi.remove(deleting.id);
			deleting = null;
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete';
		}
	}
</script>

<div class="page-head">
	<h1>Categories</h1>
	<button class="primary" onclick={() => openCreate('expense')}>+ Add Category</button>
</div>

{#if error}<div class="error">{error}</div>{/if}

<div class="grid grid-2">
	{#each [
		{ title: 'Income Categories', list: income, t: 'income' as TxType },
		{ title: 'Expense Categories', list: expense, t: 'expense' as TxType }
	] as col (col.title)}
		<div class="card">
			<div class="row" style="justify-content: space-between; margin-bottom: 8px">
				<h2>{col.title}</h2>
				<button class="small" onclick={() => openCreate(col.t)}>+ Add</button>
			</div>
			{#if col.list.length === 0}
				<div class="empty">No categories.</div>
			{:else}
				<table>
					<tbody>
						{#each col.list as c (c.id)}
							<tr>
								<td>{c.name}</td>
								<td style="text-align: right; white-space: nowrap">
									<button class="small" onclick={() => openEdit(c)}>Rename</button>
									<button class="small danger" onclick={() => (deleting = c)}>Delete</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{/if}
		</div>
	{/each}
</div>

{#if showForm}
	<Modal title={editing ? 'Edit Category' : 'Add Category'} onclose={() => (showForm = false)}>
		<div class="field">
			<label for="c-name">Name</label>
			<input id="c-name" type="text" placeholder="Groceries" bind:value={name} />
		</div>
		<div class="field">
			<label for="c-type">Type</label>
			<select id="c-type" bind:value={type}>
				<option value="expense">Expense</option>
				<option value="income">Income</option>
			</select>
		</div>
		{#if error}<div class="error">{error}</div>{/if}
		<div class="row" style="justify-content: flex-end; margin-top: 8px">
			<button onclick={() => (showForm = false)}>Cancel</button>
			<button class="primary" onclick={save}>Save</button>
		</div>
	</Modal>
{/if}

{#if deleting}
	<Modal title="Delete category?" onclose={() => (deleting = null)}>
		<p>Delete “{deleting.name}”? Categories used by transactions or budgets cannot be deleted.</p>
		<div class="row" style="justify-content: flex-end; margin-top: 16px">
			<button onclick={() => (deleting = null)}>Cancel</button>
			<button class="danger" onclick={confirmDelete}>Delete</button>
		</div>
	</Modal>
{/if}
