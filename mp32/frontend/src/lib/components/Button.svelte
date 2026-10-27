
<script lang="ts">
    import type { Snippet } from 'svelte';
    import type { HTMLAnchorAttributes, HTMLAttributes, HTMLButtonAttributes } from 'svelte/elements';
    import { cn } from '../utils';

    type Props = Omit<
        HTMLAttributes<HTMLElement>,
        'children' | 'class' | 'disabled' | 'rel' | 'target' | 'type'
    > & {
        children: Snippet;
        class?: string;
        href?: string;
        target?: HTMLAnchorAttributes['target'];
        rel?: HTMLAnchorAttributes['rel'];
        type?: HTMLButtonAttributes['type'];
        disabled?: HTMLButtonAttributes['disabled'];
        hover?: boolean;
    };

    let {
        children,
        href,
        target,
        rel,
        type,
        disabled,
        hover = true,
        class: className,
        ...rest
    }: Props = $props();

    const defaultClass =
        'btn btn-md text-xs bg-surface-500 text-surface-100 rounded-xl hover:text-black hover:bg-yellowbrand';
</script>

{#if href}
    <a
        {...rest}
        href={href}
        target={target}
        rel={target === '_blank' ? rel ?? 'noopener noreferrer' : rel}
        class={`mp32-button ${hover ? 'mp32-button-hover' : 'mp32-button-no-hover'} ${cn(defaultClass, hover ? '' : 'hover:bg-transparent hover:text-current', className)}`}
    >
        {@render children()}
    </a>
{:else}
    <button
        {...rest}
        type={type ?? 'button'}
        disabled={disabled}
        class={`mp32-button ${hover ? 'mp32-button-hover' : 'mp32-button-no-hover'} ${cn(defaultClass, hover ? '' : 'hover:bg-transparent hover:text-current', className)}`}
    >
        {@render children()}
    </button>
{/if}

<style>
    .mp32-button-hover:hover:not(:disabled) {
        background-color: var(--color-yellowbrand);
        color: black;
    }

    .mp32-button-no-hover:hover:not(:disabled) {
        background-color: transparent;
        color: inherit;
        filter: none;
    }
</style>
