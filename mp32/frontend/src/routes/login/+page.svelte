<script lang="ts">
    import { ArrowUpRight } from 'lucide-svelte';
    import Panel from '#lib/components/Panel.svelte';
    import Button from '#lib/components/Button.svelte';
    import Input from '#lib/components/Input.svelte';
</script>

<div class="min-h-screen flex items-center justify-center">
    <Panel>
        <form class="w-64 space-y-4">
            <fieldset class="space-y-2 text-surface-100">
                <legend>Login</legend>

                <label class="gap-1 flex flex-col text-xs" for="user">
                    <span>User</span>
                    <Input id="user" type="text" autocomplete="username"/>
                </label>

                <label class="gap-1 flex flex-col text-xs" for="password">
                    <span>Password</span>
                    <Input id="password" type="password" autocomplete="current-password"/>
                </label>
            </fieldset>
        </form>

        <div class="flex items-center gap-4">
            <Button href="/home">
                <span>log-in</span>
            </Button>
            <Button href="/signup" target="_blank">
                <span>sign-up</span>
                <ArrowUpRight size={16} />
            </Button>
        </div>
    </Panel>
</div>
