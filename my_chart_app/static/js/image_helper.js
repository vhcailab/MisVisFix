async function hashImageFromUrl(imageUrl) {
    try {
        // Fetch the image as an ArrayBuffer
        const response = await fetch(imageUrl);
        const imageData = await response.arrayBuffer();

        // Compute SHA-256 hash using Web Crypto API
        // const hashBuffer = await crypto.subtle.digest("SHA-256", imageData);
        // const hashArray = Array.from(new Uint8Array(hashBuffer));
        // const hashHex = hashArray.map(byte => byte.toString(16).padStart(2, "0")).join("");
        const wordArray = CryptoJS.lib.WordArray.create(new Uint8Array(imageData));
        const hashHex = CryptoJS.SHA256(wordArray).toString(CryptoJS.enc.Hex);
        console.log(`Image Hash: ${hashHex}`);
        return hashHex;
    } catch (error) {
        console.error("Error fetching image:", error.message);
        return null;
    }
}


function convertMarkdownToHTML(markdown) {
    // Convert Markdown-style bold and italics to HTML
    markdown = markdown
        .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')  // Bold **text**
        .replace(/\*(.*?)\*/g, '<i>$1</i>')      // Italic *text*
        .replace(/__(.*?)__/g, '<b>$1</b>')      // Bold __text__
        .replace(/_(.*?)_/g, '<i>$1</i>')        // Italic _text_
        .replace(/^- (.*)$/gm, '<li>$1</li>');   // List items

    // Wrap lists inside <ul> if needed
    markdown = markdown.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');

    // Convert line breaks to proper HTML
    markdown = markdown.replace(/\n/g, '<br>');

    // Use DOMParser to convert to HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(markdown, 'text/html');

    return doc.body.innerHTML;
}