// generate_puter.js
// Generates AI images using Puter.js when PUTER_AUTH_TOKEN is provided.
const fs = require('fs');
const { init } = require('@heyputer/puter.js/src/init.cjs');

async function main() {
    const prompt = process.argv[2];
    const outputPath = process.argv[3];
    const token = process.env.PUTER_AUTH_TOKEN;

    if (!token) {
        console.error("NO_PUTER_TOKEN");
        process.exit(1);
    }

    try {
        const puter = init(token);
        const models = [
            "black-forest-labs/flux-schnell",
            "black-forest-labs/flux-2-klein-4b",
            "openai/gpt-image-2.5-flare",
            "stabilityai/stable-diffusion-xl-base-1.0"
        ];
        
        let result = null;
        for (const m of models) {
            try {
                console.log(`[Puter] Attempting model: ${m}...`);
                result = await puter.ai.txt2img(prompt, { model: m });
                if (result) break;
            } catch (err) {
                console.log(`[Puter] Model ${m} failed: ${err.message || err}`);
            }
        }

        if (!result) {
            console.error("ALL_MODELS_FAILED");
            process.exit(2);
        }

        let src = result.src || (result instanceof Buffer ? result : null);
        if (typeof src === 'string' && src.startsWith('data:image')) {
            const base64Data = src.replace(/^data:image\/\w+;base64,/, "");
            fs.writeFileSync(outputPath, Buffer.from(base64Data, 'base64'));
            console.log(`[Puter] Saved image to ${outputPath}`);
            process.exit(0);
        } else if (Buffer.isBuffer(result)) {
            fs.writeFileSync(outputPath, result);
            console.log(`[Puter] Saved buffer image to ${outputPath}`);
            process.exit(0);
        } else {
            console.error("UNKNOWN_IMAGE_FORMAT");
            process.exit(3);
        }
    } catch (e) {
        console.error("PUTER_FATAL:", e.message || e);
        process.exit(4);
    }
}

main();
