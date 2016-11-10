window.onload = getChunks;

function getChunks() {
	return fetch('/chunks/_recent', 
        { 
            method: 'GET',
        })
        .then(function(response) {
            if (response.status !== 200) {
                return null;
            }
            return response.json();
        })
        .then(function(chunks) {  
            if (chunks !== null) {
                showChunks(chunks)
            }
        })
        .catch(function(err) {});
}

function showChunks(chunks) {
	clearChunks();
	for (var chunk in chunks) {
		var div = document.createElement('div');
    	div.className = "chunk";
    	div.innerText = chunks[chunk];
		document.getElementsByClassName('chunks')[0].appendChild(div);
	}
}

function clearChunks(){
    var chunks = document.getElementsByClassName('chunks')[0];
    while (chunks.hasChildNodes()) {
        chunks.removeChild(maps.firstChild);
    }
}