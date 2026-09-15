(() => {
    const script = document.currentScript;

    if (!script) {
        console.error(
            "[widget] Could not find current script."
        );
        return;
    }

    const scriptUrl = new URL(script.src);
    const widgetId = scriptUrl.searchParams.get("id");

    if (!widgetId) {
        console.error(
            "[widget] Missing widget id."
        );
        return;
    }

    const apiBaseUrl = scriptUrl.origin;

    async function loadWidget() {
        try {
            const response = await fetch(
                `${apiBaseUrl}/public/widgets/${widgetId}/config`
            );

            if (!response.ok) {
                throw new Error(
                    `Config request failed: ${response.status}`
                );
            }

            const config = await response.json();

            renderWidget(config);

        } catch (error) {
            console.error(
                "[widget] Failed to load:",
                error
            );
        }
    }


    function renderWidget(config) {
        const container = document.createElement("div");

        container.setAttribute(
            "data-widget-id",
            widgetId
        );

        const title = document.createElement("h3");
        title.textContent = config.title;

        container.appendChild(title);

        if (config.description) {
            const description =
                document.createElement("p");

            description.textContent =
                config.description;

            container.appendChild(description);
        }

        const form = document.createElement("form");

        for (const field of config.fields) {
            const wrapper =
                document.createElement("div");

            const label =
                document.createElement("label");

            label.textContent = field.label;

            let input;

            if (
                field.type === "textarea" ||
                field.name === "message"
            ) {
                input =
                    document.createElement("textarea");
            } else {
                input =
                    document.createElement("input");

                input.type =
                    field.type === "email"
                        ? "email"
                        : "text";
            }

            input.name = field.name;

            if (field.required) {
                input.required = true;
            }

            wrapper.appendChild(label);
            wrapper.appendChild(input);

            form.appendChild(wrapper);
        }

        const honeypot =
            document.createElement("input");

        honeypot.type = "text";
        honeypot.name = "website";
        honeypot.tabIndex = -1;
        honeypot.autocomplete = "off";
        honeypot.style.position = "absolute";
        honeypot.style.left = "-9999px";

        form.appendChild(honeypot);

        const button =
            document.createElement("button");

        button.type = "submit";
        button.textContent =
            config.button_text;

        form.appendChild(button);

        const status =
            document.createElement("p");

        form.appendChild(status);

        let pendingIdempotencyKey = null;

        form.addEventListener(
            "submit",
            async (event) => {
                event.preventDefault();

                button.disabled = true;
                status.textContent = "Sending...";

                if (!pendingIdempotencyKey) {
                    pendingIdempotencyKey =
                        crypto.randomUUID();
                }

                const payload = {};

                for (const field of config.fields) {
                    const element =
                        form.elements[field.name];

                    payload[field.name] =
                        element.value;
                }

                try {
                    const response = await fetch(
                        `${apiBaseUrl}/public/widgets/${widgetId}/submissions`,
                        {
                            method: "POST",
                            headers: {
                                "Content-Type":
                                    "application/json",
                                "Idempotency-Key":
                                    pendingIdempotencyKey
                            },
                            body: JSON.stringify({
                                payload,
                                honeypot:
                                    honeypot.value
                            })
                        }
                    );

                    const data =
                        await response.json();

                    if (!response.ok) {
                        status.textContent =
                            `Error: ${JSON.stringify(data)}`;

                        return;
                    }

                    status.textContent =
                        "Submitted successfully.";

                    pendingIdempotencyKey = null;

                    form.reset();

                } catch (error) {
                    console.error(
                        "[widget] Submission failed:",
                        error
                    );

                    status.textContent =
                        "Network error. Please retry.";

                } finally {
                    button.disabled = false;
                }
            }
        );

        container.appendChild(form);

        script.insertAdjacentElement(
            "afterend",
            container
        );
    }


    loadWidget();
})();