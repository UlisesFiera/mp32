<script lang="ts">
    import { page } from '$app/state';
    import { fade } from 'svelte/transition';
    import Button from '#lib/components/Button.svelte';
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

    const navButtonClass = 'group w-full h-7 justify-start gap-3 bg-transparent p-0';
    const iconClass = 'grid size-7 shrink-0 place-items-center rounded-xs bg-white/20 \
        text-xs transition-colors duration-1000 ease-in-out group-hover:duration-100 \
        group-hover:bg-yellowbrand group-hover:text-black motion-reduce:transition-none';
</script>

<div class="flex min-h-screen bg-neutral-950 text-surface-100">

    <!-- sidebar -->
    <aside class={`relative flex shrink-0 flex-col justify-between px-5 pb-5 pt-8 transition-[width]
        md:pt-10
        duration-500 ease-in-out motion-reduce:transition-none
        after:pointer-events-none after:absolute after:right-0
        after:top-4 after:bottom-4 after:w-px after:bg-white/10
        ${collapsed ? 'w-20' : 'w-50'}`}>
        <nav class="flex flex-col gap-2" aria-label="Main navigation">
            {#each links as link}

                <!-- buttons -->
                <Button
                    href={link.href}
                    hover={false}
                    aria-label={link.label}
                    title={collapsed ? link.label : undefined}
                    aria-current={page.url.pathname === link.href ? 'page' : undefined}
                    class={navButtonClass}>

                    <!-- icon badge -->
                    <span class={`${iconClass} ${page.url.pathname === link.href 
                        ? 'bg-yellowbrand text-black' : ''}`}>
                        {link.label.slice(0, 1)}
                    </span>

                    <!-- name -->
                    <span
                        aria-hidden={collapsed}
                        class={`block overflow-hidden whitespace-nowrap
                            transition-[max-width,opacity,color] duration-1000 ease-in-out
                            group-hover:duration-100 group-hover:text-yellowbrand
                            motion-reduce:transition-none
                            ${collapsed ? 'max-w-0 opacity-0' : 'max-w-32 opacity-100'}
                            ${page.url.pathname === link.href ? 'text-yellowbrand' : ''}`}>
                        {link.label}
                    </span>
                </Button>
            {/each}
        </nav>

        <div class="relative flex h-7 items-center">

            <!-- logo -->
            {#if !collapsed}
                <span class="text-sm" in:fade={{ duration: 250, delay: 500 }} out:fade={{ duration: 250 }}>
                    mp32
                </span>
            {/if}

            <!-- collapse button -->
            <Button
                hover={false}
                class={`group absolute top-0 size-7 justify-center rounded-xs 
                    bg-transparent p-0 text-xs leading-none transition-[left] 
                    duration-400 ease-in-out motion-reduce:transition-none
                    ${collapsed ? 'left-0' : 'left-[calc(100%-1.75rem)]'}`}
                onclick={() => collapsed = !collapsed}
                aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                aria-expanded={!collapsed}>
                <span class={iconClass}>{collapsed ? '›' : '‹'}</span>
            </Button>
        </div>
    </aside>

    <main class="min-w-0 flex-1 p-6 md:p-10">
        {@render children()}
    </main>
</div>
