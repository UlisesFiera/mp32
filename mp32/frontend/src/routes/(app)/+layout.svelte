<script lang="ts">
    import { page } from '$app/state';
    import type { LayoutProps } from './$types';

    let { children }: LayoutProps = $props();
    let collapsed = $state(false);

    const links = [
        { label: 'Home', href: '/home' },
        { label: 'Collection', href: '/collection' },
        { label: 'Pair', href: '/pair' },
        { label: 'Explore', href: '/explore' },
        { label: 'Mix', href: '/mix' }
    ];
</script>

<div class="flex min-h-screen bg-neutral-950 text-surface-100">
    <aside class={`flex shrink-0 flex-col border-r border-white/10 bg-neutral-900/80 p-3 transition-[width] duration-200 ${collapsed ? 'w-16' : 'w-64'}`}>
        <div class="mb-6 flex items-center justify-between gap-2 px-2 py-2">
            {#if !collapsed}<span class="font-title text-sm">mp32</span>{/if}
            <button
                type="button"
                class="grid size-8 place-items-center rounded-lg text-white/70 hover:bg-white/10 hover:text-white"
                onclick={() => collapsed = !collapsed}
                aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                aria-expanded={!collapsed}
            >
                {collapsed ? '›' : '‹'}
            </button>
        </div>

        <nav class="flex flex-col gap-1" aria-label="Main navigation">
            {#each links as link}
                <a
                    href={link.href}
                    aria-label={link.label}
                    title={collapsed ? link.label : undefined}
                    aria-current={page.url.pathname === link.href ? 'page' : undefined}
                    class={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors ${page.url.pathname === link.href ? 'bg-white/10 text-white' : 'text-white/65 hover:bg-white/5 hover:text-white'}`}
                >
                    <span class="grid size-7 shrink-0 place-items-center rounded-lg bg-white/5 text-xs font-semibold">{link.label.slice(0, 1)}</span>
                    {#if !collapsed}<span>{link.label}</span>{/if}
                </a>
            {/each}
        </nav>
    </aside>

    <main class="min-w-0 flex-1 p-6 md:p-10">
        {@render children()}
    </main>
</div>
