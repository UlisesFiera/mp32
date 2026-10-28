
<script lang="ts">
    import type { Snippet } from 'svelte';
    import type { HTMLAnchorAttributes } from 'svelte/elements';

    type Props = {
        children: Snippet;
        href?: string;
        target?: HTMLAnchorAttributes['target'];
    };

    let { children, href, target }: Props = $props();

    const buttonClass =
        'btn btn-md text-xs bg-surface-500 text-surface-100 \
        rounded-xs transition-colors duration-1000 ease-in-out hover:duration-100 \
        hover:text-black hover:bg-yellowbrand motion-reduce:transition-none';
</script>

{#if href}
    <a
        href={href}
        target={target}
        rel={target === '_blank' ? 'noopener noreferrer' : undefined}
        class={buttonClass}
    >
        {@render children()}
    </a>
{:else}
    <button
        type="button"
        class={buttonClass}
    >
        {@render children()}
    </button>
{/if}
