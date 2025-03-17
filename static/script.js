async function generateSong() {
    let theme = document.getElementById("theme").value.trim();
    if (!theme) {
        alert("Please enter a theme.");
        return;
    }

    document.getElementById("lyrics").innerText = "Generating...";
    document.getElementById("generateButton").disabled = true;

    try {
        let response = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ theme: theme }),
        });

        let data = await response.json();
        document.getElementById("lyrics").innerText = data.lyrics;

        if (data.music) {
            document.getElementById("musicPlayer").src = data.music;
            document.getElementById("musicPlayer").style.display = "block";
            document.getElementById("downloadMusic").href = data.music;
            document.getElementById("downloadMusic").style.display = "inline-block";
        }

        if (data.lyrics_audio) {
            document.getElementById("lyricsAudioPlayer").src = data.lyrics_audio;
            document.getElementById("lyricsAudioPlayer").style.display = "block";
            document.getElementById("downloadLyricsAudio").href = data.lyrics_audio;
            document.getElementById("downloadLyricsAudio").style.display = "inline-block";
        }

    } catch (error) {
        alert("An error occurred.");
    } finally {
        document.getElementById("generateButton").disabled = false;
    }
}
