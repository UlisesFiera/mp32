<script lang="ts">
    import Panel from '#lib/components/Panel.svelte';
    import Button from '#lib/components/Button.svelte';
    import Input from '#lib/components/Input.svelte';
</script>

<div class="min-h-screen flex items-center justify-center">
    <Panel>
        <form class="w-64 space-y-4">
            <fieldset class="space-y-2 text-surface-100">
                <legend>Sign up</legend>

                <label class="gap-1 flex flex-col text-xs" for="name">
                    <span>Name</span>
                    <Input id="name" type="text" autocomplete="name"/>
                </label>

                <label class="gap-1 flex flex-col text-xs" for="user">
                    <span>User</span>
                    <Input id="user" type="text" autocomplete="username"/>
                </label>

                <label class="gap-1 flex flex-col text-xs" for="email">
                    <span>Email</span>
                    <Input id="email" type="email" autocomplete="email"/>
                </label>

                <label class="gap-1 flex flex-col text-xs" for="password">
                    <span>Password</span>
                    <Input id="password" type="password" autocomplete="new-password"/>
                </label>
            </fieldset>

            <div class="flex items-center gap-4">
                <Button>
                    <span>create account</span>
                </Button>
                <Button href="/login">
                    <span>back to log-in</span>
                </Button>
            </div>
        </form>
    </Panel>
</div>
