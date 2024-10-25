let currentlyPlayingAudio = null;

document.addEventListener('DOMContentLoaded', () => {
    const rockPopList = document.getElementById('rock-pop-list');
    const classicalList = document.getElementById('classical-list');
    const filmList = document.getElementById('film-list');
    const jazzList = document.getElementById('jazz-list');
    const traditionalList = document.getElementById('traditional-list');
    const tangoList = document.getElementById('tango-list');

    fetch('assets/json/pop-rock-rep.json')
    .then(response => response.json())
    .then(data => {
        for (const artist in data) {
            if (data.hasOwnProperty(artist)) {
                const songs = data[artist].songs;
                songs.forEach(song => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${artist} - ${song.title}`;
                    
                    if (song.mp3_file) {
                        listItem.innerHTML += ` <i class="fas fa-volume-low" data-src="assets/audio/${song.mp3_file}"></i>`;
                        listItem.querySelector('i').addEventListener('click', () => toggleAudio(listItem, song.mp3_file));
                    }
                    
                    rockPopList.appendChild(listItem);
                });
            }
        }
    })
    .catch(error => console.error('Error fetching pop/rock data:', error));


        fetch('assets/json/classical-rep.json')
        .then(response => response.json())
        .then(data => {
            for (const composer in data) {
                if (data.hasOwnProperty(composer)) {
                    const compositions = data[composer].songs;
                    compositions.forEach(composition => {
                        const listItem = document.createElement('li');
    
                        if (composition.mp3_file) {
                            listItem.innerHTML = `${composer} - ${composition.title} <i class="fas fa-volume-low" data-src="assets/audio/${composition.mp3_file}"></i>`;
                            listItem.querySelector('i').addEventListener('click', () => toggleAudio(listItem, composition.mp3_file));
                        } else {
                            listItem.textContent = `${composer} - ${composition.title}`;
                        }
    
                        classicalList.appendChild(listItem);
                    });
                }
            }
        })
        .catch(error => console.error('Error fetching classical data:', error));
    

        fetch('assets/json/film-musical-games-rep.json')
        .then(response => response.json())
        .then(data => {
            for (const composer in data) {
                if (data.hasOwnProperty(composer)) {
                    const compositions = data[composer].songs;
                    compositions.forEach(composition => {
                        const listItem = document.createElement('li');
    
                        if (composition.mp3_file) {
                            listItem.innerHTML = `${composer} - ${composition.title} <i class="fas fa-volume-low" data-src="assets/audio/${composition.mp3_file}"></i>`;
                            listItem.querySelector('i').addEventListener('click', () => toggleAudio(listItem, composition.mp3_file));
                        } else {
                            listItem.textContent = `${composer} - ${composition.title}`;
                        }
    
                        filmList.appendChild(listItem);
                    });
                }
            }
        })
        .catch(error => console.error('Error fetching film data:', error));
    

    fetch('assets/json/jazz-rep.json')
        .then(response => response.json())
        .then(data => {
            for (const composer in data) {
                if (data.hasOwnProperty(composer)) {
                    const compositions = data[composer].songs;
                    compositions.forEach(composition => {
                        const listItem = document.createElement('li');

                        if (composition.mp3_file) {
                            listItem.innerHTML = `${composer} - ${composition.title} <i class="fas fa-volume-low" data-src="assets/audio/${composition.mp3_file}"></i>`;
                            listItem.querySelector('i').addEventListener('click', () => toggleAudio(listItem, composition.mp3_file));
                        } else {
                            listItem.textContent = `${composer} - ${composition.title}`;
                        }

                        jazzList.appendChild(listItem);
                    });
                }
            }
        })
        .catch(error => console.error('Error fetching jazz data:', error));

        fetch('assets/json/traditional-rep.json')
        .then(response => response.json())
        .then(data => {
            for (const composer in data) {
                if (data.hasOwnProperty(composer)) {
                    const compositions = data[composer].songs;
                    compositions.forEach(composition => {
                        const listItem = document.createElement('li');
    
                        if (composition.mp3_file) {
                            listItem.innerHTML = `${composer} - ${composition.title} <i class="fas fa-volume-low" data-src="assets/audio/${composition.mp3_file}"></i>`;
                            listItem.querySelector('i').addEventListener('click', () => toggleAudio(listItem, composition.mp3_file));
                        } else {
                            listItem.textContent = `${composer} - ${composition.title}`;
                        }
    
                        traditionalList.appendChild(listItem);
                    });
                }
            }
        })
        .catch(error => console.error('Error fetching traditional data:', error));

        fetch('assets/json/tango-rep.json')
        .then(response => response.json())
        .then(data => {
            for (const composer in data) {
                if (data.hasOwnProperty(composer)) {
                    const compositions = data[composer].songs;
                    compositions.forEach(composition => {
                        const listItem = document.createElement('li');

                        if (composition.mp3_file) {
                            listItem.innerHTML = `${composer} - ${composition.title} <i class="fas fa-volume-low" data-src="assets/audio/${composition.mp3_file}"></i>`;
                            listItem.querySelector('i').addEventListener('click', () => toggleAudio(listItem, composition.mp3_file));
                        } else {
                            listItem.textContent = `${composer} - ${composition.title}`;
                        }

                        tangoList.appendChild(listItem);
                    });
                }
            }
        })
        .catch(error => console.error('Error fetching jazz data:', error));

        function toggleAudio(listItem, mp3File) {
            const icon = listItem.querySelector('i');
        
            // Check if there is currently playing audio
            if (currentlyPlayingAudio && currentlyPlayingAudio.audio) {
                // Pause the currently playing audio
                currentlyPlayingAudio.audio.pause();
                // Reset the class of the previous icon
                const previousIcon = currentlyPlayingAudio.listItem.querySelector('i');
                previousIcon.classList.remove('text-danger', 'fa-volume-up');
            }
        
            // Check if the user clicked the same icon again
            if (currentlyPlayingAudio && currentlyPlayingAudio.audio && currentlyPlayingAudio.audio.src.includes(mp3File)) {
                // If yes, set currentlyPlayingAudio to null
                currentlyPlayingAudio = null;
            } else {
                // Create a new Audio instance and play the selected audio
                const audio = new Audio(`assets/audio/${mp3File}`);
                audio.play();
                currentlyPlayingAudio = {
                    audio: audio,
                    listItem: listItem
                };
        
                // Add the classes to the new icon
                console.log('Playing:', mp3File);
                icon.classList.add('fa-volume-up', 'text-danger');
            }
        }
        
        
});
