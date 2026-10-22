
<script lang="ts">
    import type { Snippet } from 'svelte';
    import type { HTMLAnchorAttributes } from 'svelte/elements';

    let {
        children,
        href,
        target,
    }: {
        children: Snippet;
        href?: string;
        target?: HTMLAnchorAttributes['target'];
    } = $props();
</script>

{#if href}
    <a href={href} target={target} rel={target === '_blank' ? 'noopener noreferrer' : undefined} 
        class="btn text-xs bg-surface-500 text-surface-100 rounded-xl hover:text-black hover:bg-yellowbrand">
        {@render children()}
    </a>
{:else}
    <button type="button" class="btn text-xs bg-surface-500 text-surface-100 rounded-xl hover:text-black hover:bg-yellowbrand">
        {@render children()}
    </button>
{/if}
