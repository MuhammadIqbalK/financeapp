<script lang="ts">
	import { auth } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';

	let mode = $state<'login' | 'register'>('login');
	let email = $state('');
	let password = $state('');
	let error = $state('');
	let busy = $state(false);

	async function submit(e: Event) {
		e.preventDefault();
		error = '';
		busy = true;
		try {
			if (mode === 'login') await auth.login(email, password);
			else await auth.register(email, password);
			goto('/dashboard');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Something went wrong';
		} finally {
			busy = false;
		}
	}
</script>

<div class="auth-page">
	<div class="auth-card">
		<h1>Personal Finance</h1>
		<div class="sub">
			{mode === 'login' ? 'Sign in to your account' : 'Create a new account'}
		</div>

		<form onsubmit={submit}>
			<div class="field">
				<label for="email">Email</label>
				<input id="email" type="email" required bind:value={email} placeholder="you@example.com" />
			</div>
			<div class="field">
				<label for="password">Password</label>
				<input
					id="password"
					type="password"
					required
					minlength="6"
					bind:value={password}
					placeholder="••••••••"
				/>
			</div>

			{#if error}<div class="error">{error}</div>{/if}

			<button class="primary" type="submit" disabled={busy} style="width: 100%; margin-top: 6px">
				{busy ? 'Please wait…' : mode === 'login' ? 'Login' : 'Register'}
			</button>
		</form>

		<div class="muted" style="margin-top: 16px; text-align: center; font-size: 13px">
			{mode === 'login' ? "Don't have an account?" : 'Already have an account?'}
			<button
				class="ghost"
				style="color: var(--accent); font-weight: 600"
				onclick={() => {
					mode = mode === 'login' ? 'register' : 'login';
					error = '';
				}}
			>
				{mode === 'login' ? 'Register' : 'Login'}
			</button>
		</div>
	</div>
</div>
