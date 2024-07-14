
    $(document).ready(function () {
      $(".custom-carousel").owlCarousel({
        autoWidth: true,
        loop: true
      });

      $(".custom-carousel .item").click(function () {
        $(".custom-carousel .item").not($(this)).removeClass("active");
        $(this).toggleClass("active");
        $(this).toggleClass("active");
      });
    });
document.getElementById('cancelButton').addEventListener('click', function() {
  $('#loginModal').modal('hide');
});
document.getElementById('Button').addEventListener('click', function() {
    fetch('/check_login')
        .then(response => response.json())
        .then(data => {
            if (data.logged_in) {
                // Proceed with file upload
                handleFileUploadProcess();
            } else {
                // Show Bootstrap modal
                $('#loginModal').modal('show');
                // Redirect to login page when "Log In" button in modal is clicked
                document.getElementById('loginModalRedirect').addEventListener('click', function() {
                    window.location.href = '/login';
                });
            }
        })
        .catch(error => {
            console.error('Error checking login status:', error);
            // Fallback to login page on error
            window.location.href = '/login';
        });
});
    const formContainer = document.getElementById('form-container');
    const infoPopup = document.querySelector('.form-popup');
    const containerUpload = document.querySelector('.container_upload');
    let animationTimeout;
function validateInputs() {
        const number = document.getElementById('exampleInputnumber').value.trim();
        const school = document.getElementById('exampleInputSchool').value.trim();
        const name = document.getElementById('exampleInputName').value.trim();
        const email = document.getElementById('exampleInputEmail').value.trim();
        const memoirFiles = document.getElementById('memoir-files').files.length;
        const correctionFiles = document.getElementById('correction-attestation').files.length;
        return (number && school && name && email && memoirFiles > 0 && correctionFiles > 0);
    }

    function togglePublishButton() {
        const publishButton = document.getElementById('publishButton');
        publishButton.style.display = validateInputs() ? 'block' : 'none';
    }
async function uploadFiles(studentData) {
        const memoirFiles = document.getElementById('memoir-files').files[0];
        const correctionAttestation = document.getElementById('correction-attestation').files[0];
        const formData = new FormData();
        formData.append('memoir_files', memoirFiles);
        formData.append('correction_attestation', correctionAttestation);
        formData.append('student_number', studentData.student_number);
        formData.append('school', studentData.school);
        formData.append('name', studentData.name);
        formData.append('email', studentData.email);

        try {
            const response = await fetch('/submit_student_info', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Extracted data:', result);
                populateForm(result);
                formContainer.style.display = 'none';
                infoPopup.style.display = 'flex';
                document.body.classList.add('overlay-active');
            } else {
                const errorData = await response.json();
                console.error('Error uploading file:', errorData);
                alert('File upload failed: ' + (errorData.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error uploading files:', error);
        }
    }

    function populateForm(data) {
        document.getElementById('exampleInputTitle').value = data.title || '';
        document.getElementById('exampleInputAuthor').value = data.name || '';
        document.getElementById('exampleInputMention').value = data.mention || '';
        document.getElementById('exampleInputUniversity').value = data.university || '';
        document.getElementById('exampleInputEcole').value = data.ecole || '';
        document.getElementById('exampleInputDate').value = data.date || '';
        document.getElementById('exampleInputTheme').value = data.theme || '';
    }

    function toggleEdit() {
        console.log("Editer button clicked");
        const inputs = document.querySelectorAll('.upload-form input');
        inputs.forEach(input => {
            input.readOnly = !input.readOnly;
        });
    }
    console.log("Toggle button")

    document.getElementById('exampleInputnumber').addEventListener('input', togglePublishButton);
    document.getElementById('exampleInputSchool').addEventListener('input', togglePublishButton);
    document.getElementById('exampleInputName').addEventListener('input', togglePublishButton);
    document.getElementById('exampleInputEmail').addEventListener('input', togglePublishButton);
    document.getElementById('memoir-files').addEventListener('change', togglePublishButton);
    document.getElementById('correction-attestation').addEventListener('change', togglePublishButton);

document.querySelector('.upload').addEventListener('click', async function() {
        console.log('Upload button clicked');
        const studentData = {
            student_number: document.getElementById('exampleInputnumber').value.trim(),
            school: document.getElementById('exampleInputSchool').value.trim(),
            name: document.getElementById('exampleInputName').value.trim(),
            email: document.getElementById('exampleInputEmail').value.trim()
        };

        containerUpload.classList.add("active");
        animationTimeout = setTimeout(() => {
            containerUpload.classList.remove("active");
            infoPopup.style.display = 'block';
            document.querySelector('.frame').style.display = 'none';
        }, 4000); // 3 seconds animation

        await uploadFiles(studentData);
    });

function handleFileUploadProcess() {
    const container_upload = document.querySelector(".container_upload"),
        uploadButton = document.querySelector('.upload'),
        formPopup = document.querySelector('.form-popup'),
        fileName = document.querySelector("#file-name");
    const formContainer = document.getElementById('form-container');

    let animationTimeout;

    function handleFileUpload(input) {
        const file = input.files[0];
        fileName.textContent = file ? file.name : "No file selected";
        if (file) {
            uploadButton.style.display = 'block';
        } else {
            uploadButton.style.display = 'none';
        }
    }


    document.getElementById("Button").addEventListener("click", function () {
        document.querySelector('.frame').style.display = 'block';
        document.querySelector('.container_upload').style.display = 'flex';
        document.querySelector('.navbar').classList.add('blur');
        document.querySelector('.books').classList.add('blur');
        document.querySelector('.mention_section').classList.add('blur');
        document.querySelector('.wrapper').classList.add('blur');
    });

    document.querySelector('.btn-close').addEventListener('click', function () {
        document.querySelector('.frame').style.display = 'none';
        document.querySelector('.container_upload').style.display = 'none';
        document.querySelector('.navbar').classList.remove('blur');
        document.querySelector('.books').classList.remove('blur');
        document.querySelector('.mention_section').classList.remove('blur');
        document.querySelector('.wrapper').classList.remove('blur');
        clearTimeout(animationTimeout); // Clear animation timeout
        container_upload.classList.remove("active"); // Remove animation class
    });

    document.querySelector('.frame').addEventListener('click', function (e) {
        if (e.target.classList.contains('frame')) {
            this.style.display = 'none';
            document.querySelector('.navbar').classList.remove('blur');
            document.querySelector('.wrapper').classList.remove('blur');
            document.querySelector('.mention_section').classList.add('blur');
            clearTimeout(animationTimeout); // Clear animation timeout
            container_upload.classList.remove("active"); // Remove animation class
        }
    });

    document.querySelector('.form-popup .btn-close').addEventListener('click', function () {
        document.querySelector('.form-popup').style.display = 'none';
        document.querySelector('.frame').style.display = 'block';
    });

    $(document).ready(function(){
        $('#browseSelect').popover({
            html: true,
            content: function () {
                return $(this).data('content');
            }
        });

        $(document).on('click', '#browseSelect + .popover .popover-body a', function(e) {
            e.preventDefault();
            var selectedValue = $(this).attr('data-value');
            $('#browseSelect').val(selectedValue);
            $('#browseSelect').popover('hide');
        });
    });

$(".default_option").click(function(){
    console.log("Here");
    $(".dropdown ul").addClass("active");
});
}

$(".dropdown ul li").click(function(){
  var text = $(this).text();
  $(".default_option").text(text);
  $(".dropdown ul").removeClass("active");
});
function handleFileUpload(input) {
            const fileNameSpan = document.getElementById('file-name');
            const uploadButton = document.querySelector('.upload');
            fileNameSpan.textContent = input.files[0].name;
            uploadButton.style.display = 'block';
        }

async function uploadFile() {
    const fileInput = document.getElementById('fileID');
    const username = document.getElementById('usernameInput')
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('username', username.value);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const result = await response.json();
        console.log('Extracted data:', result);  // Debugging: Print the received data
        populateForm(result);
        document.querySelector('.form-popup').style.display = 'block';
    } else if (response.status === 409) {
        const errorData = await response.json();
        console.error('Error uploading file:', errorData.message);  // Debugging: Print the error message
        alert('File upload failed: ' + errorData.message);
        // Prevent further processing
    } else {
        const errorData = await response.json();
        console.error('Error uploading file:', errorData.message);  // Debugging: Print the error message
        alert('File upload failed: ' + errorData.message);
    }
    }
function populateForm(data) {
    document.getElementById('exampleInputTitle').value = data.title || '';
    document.getElementById('exampleInputAuthor').value = data.name || '';
    document.getElementById('exampleInputMention').value = data.mention || '';
    document.getElementById('exampleInputUniversity').value = data.university || '';
    document.getElementById('exampleInputEcole').value = data.ecole || '';
    document.getElementById('exampleInputDate').value = data.date || '';
    document.getElementById('exampleInputTheme').value = data.theme || '';
}

function closeForm() {
    document.querySelector('.form-popup').style.display = 'none';
}


document.querySelector('.validate').addEventListener('click', async function () {
    const memoirFilesInput = document.getElementById('memoir-files');
        const memoirFiles = memoirFilesInput.files;

        if (memoirFiles.length === 0) {
            alert('Please select a file');
            return;
        }
    const data = {
            filename: memoirFiles[0].name,
            title: document.getElementById('exampleInputTitle').value,
            author: document.getElementById('exampleInputAuthor').value,
            mention: document.getElementById('exampleInputMention').value,
            date: document.getElementById('exampleInputDate').value,
            university: document.getElementById('exampleInputUniversity').value,
            ecole: document.getElementById('exampleInputEcole').value,
            mapped_classes: document.getElementById('exampleInputMention').value,
            theme: document.getElementById('exampleInputTheme').value
        };

    try {
            const response = await fetch('/save2', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                Swal.fire({
                    title: 'Demande reçue!',
                    text: 'Nous avons reçu votre demande. Notre bibliothécaire vous répondra dans les plus brefs délais.',
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then(() => {
                    closeForm();
                });

            } else {
                const errorData = await response.json();
                Swal.fire({
                    title: 'Erreur',
                    text: 'Erreur lors de l\'enregistrement des données : ' + errorData.message,
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            }
        } catch (error) {
    Swal.fire({
        title: 'Erreur',
        text: 'Échec de l\'enregistrement des données. Veuillez réessayer.',
        icon: 'error',
        confirmButtonText: 'OK'
    }).then(() => {
            // You can add code here to be executed after the error modal is closed
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
  const dropdown = document.querySelector('.dropdown');
  const defaultOption = document.querySelector('.default_option');
  const options = document.querySelectorAll('.dropdown ul li');
  const searchInput = document.getElementById('search-input');
  const searchHistoryDropdown = document.querySelector('.dropdown-content');
  let selectedOption = 'Nom'; // Initialize selectedOption

  options.forEach(option => {
    option.addEventListener('click', function () {
      defaultOption.innerText = this.innerText;
      selectedOption = this.getAttribute('data-value');
      dropdown.classList.toggle('active'); // Toggle the dropdown class
    });
  });

  // Combine event listeners to handle clicks outside of dropdowns
  document.addEventListener('click', function (event) {
    // Hide search type dropdown if clicking outside
    if (!dropdown.contains(event.target) && !event.target.closest('.dropdown')) {
      dropdown.classList.remove('active');
    }

    // Hide search history dropdown if clicking outside
    if (!searchHistoryDropdown.contains(event.target) && !event.target.closest('.dropdown-content') && event.target !== searchInput) {
      searchHistoryDropdown.style.display = 'none';
    }
  });

  searchInput.addEventListener('input', function () {
    const query = this.value.trim();
    if (query) {
      // Fetch search history based on user input
      const user_id = document.getElementById('usernameInput').value;
      fetch(`/search_history?user_id=${user_id}&search_type=${selectedOption}`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          // Clear previous search history dropdown items
          searchHistoryDropdown.innerHTML = '';
          // Populate dropdown with search history items
          data.forEach(item => {
            const suggestion = document.createElement('div');
            const queryLink = document.createElement('a');
            queryLink.textContent = item.query;
            queryLink.href = '#'; // Replace '#' with appropriate link if available
            queryLink.classList.add('search-suggestion');
            const queryText = document.createElement('span');
            queryText.textContent = item.query;
            queryLink.addEventListener('mouseenter', function () {
              // Change background color on hover
              queryLink.style.backgroundColor = 'rgba(211, 211, 211, 0.5)';
            });
            queryLink.addEventListener('mouseleave', function () {
              // Restore background color when mouse leaves
              queryLink.style.backgroundColor = '';
            });
            queryLink.addEventListener('click', function (event) {
              event.preventDefault(); // Prevent the link from navigating
              // Set the selected suggestion as the search input value
              searchInput.value = item.query;
              // Hide the search history dropdown
              searchHistoryDropdown.style.display = 'none';
            });
            const removeButton = document.createElement('button');
            removeButton.textContent = 'x'; // Close icon
            removeButton.classList.add('remove-history');
            removeButton.addEventListener('click', function (event) {
              event.stopPropagation(); // Prevent the click from triggering other events
              fetch('/remove_history', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: user_id, query: item.query, search_type: selectedOption }),
              })
                .then(response => {
                  if (!response.ok) {
                    throw new Error('Network response was not ok');
                  }
                  return response.json();
                })
                .then(data => {
                  if (data.success) {
                    // Remove the suggestion from the dropdown
                    suggestion.remove();
                  } else {
                    console.error('Error removing history:', data.message);
                  }
                })
                .catch(error => {
                  console.error('Error removing history:', error);
                });
            });
            suggestion.appendChild(queryText);
            suggestion.appendChild(removeButton);
            searchHistoryDropdown.appendChild(suggestion);
          });
          // Display the search history dropdown
          searchHistoryDropdown.style.display = 'block';
        })
        .catch(error => {
          console.error('Error fetching search history:', error);
        });
    } else {
      // Hide the search history dropdown if search input is empty
      searchHistoryDropdown.style.display = 'none';
    }
  });
});

document.addEventListener('DOMContentLoaded', function () {
    const dropdown = document.querySelector('.dropdown');
    const defaultOption = document.querySelector('.default_option');
    const options = document.querySelectorAll('.dropdown ul li');
    const searchButton = document.querySelector('.search_field i');
    const searchInput = document.getElementById('search-input');
    const searchResultsContainer = document.querySelector('.search-results'); // Initialize searchResultsContainer
    let selectedOption = 'Nom';
     defaultOption.addEventListener('click', function () {
        dropdown.querySelector('ul').classList.toggle('active');
    });

    dropdown.addEventListener('click', function () {
        this.querySelector('ul').classList.toggle('show');
    });

    options.forEach(option => {
        option.addEventListener('click', function () {
            defaultOption.innerText = this.innerText;
            selectedOption = this.getAttribute('data-value');
            dropdown.querySelector('ul').classList.remove('active');
        });
    });

    searchButton.addEventListener('click', function (event) {
        event.preventDefault();
        const query = searchInput.value;
        console.log(query);
        const user_id = document.getElementById('usernameInput').value
        if (query) {
            const searchPayload = {
                user_id: user_id,
                search_type: selectedOption,
                search_query: query
            };
            console.log(searchPayload)
            fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ search_type: selectedOption, search_query: query }),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Received data:', data); // Log the response data for debugging
                renderSearchResults(data.result_list); // Call a function to render search results
            })
            .catch(error => {
                // Handle errors here
                console.error('Error:', error);
            });
            // Save the search history
            fetch('/save_search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchPayload),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Search history saved:', data); // Log the response data for debugging
            })
            .catch(error => {
                console.error('Error saving search history:', error);
            });

            searchInput.value = '';
            defaultOption.textContent = 'Parcourir';
            selectedOption = 'Nom';
        } else {
            // Handle case where query is empty
            console.error('Query is empty');
        }
    });

function renderSearchResults(data) {
    searchResultsContainer.innerHTML = '';
    // Create and append label for search results
    const searchResultsLabel = document.createElement('h2');
    searchResultsLabel.textContent = "Résultat(s) de la recherche";
    searchResultsLabel.style.fontFamily = 'Montserrat'; // Set Montserrat font family
    searchResultsLabel.style.fontWeight = 'normal'; // Set normal font weight
    searchResultsContainer.appendChild(searchResultsLabel);
    // Iterate over the search results and create HTML elements for each result
    data.forEach(result => {
        // Create elements for displaying search results
        const card = document.createElement('div');
        card.className = 'card bg-light-subtle mb-3';

        const img = document.createElement('img');
        img.src = `data:image/png;base64,${result.cover_image_base64}`;
        img.className = 'card-img';
        img.alt = '...';

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';

        const textSection = document.createElement('div');
        textSection.className = 'text-section';

        const title = document.createElement('h6');
        title.className = 'card-title';
        title.style = 'overflow-wrap: break-word; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;';
        title.innerText = result.title;

        const author = document.createElement('h6');
        author.className = 'card-title';
        author.innerText = result.author;

        const mention = document.createElement('p');
        mention.className = 'card-text';
        mention.style = 'overflow-wrap: break-word; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;';
        mention.innerText = result.mention;

        const theme = document.createElement('p');
        theme.className = 'card-text';
        theme.style = 'overflow-wrap: break-word; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;';

        theme.innerText = result.theme;

        const date = document.createElement('p');
        date.className = 'card-text';
        date.innerText = result.date;

        const ctaSection = document.createElement('div');
        ctaSection.className = 'cta-section d-flex justify-content-end';

        const downloadLink = document.createElement('a');
        downloadLink.href = result.download_link;
        downloadLink.className = 'btn btn-dark';
        downloadLink.innerText = 'Download';

        // Append elements
        ctaSection.appendChild(downloadLink);
        textSection.appendChild(title);
        textSection.appendChild(author);
        textSection.appendChild(mention);
        textSection.appendChild(theme);
        textSection.appendChild(date);
        cardBody.appendChild(textSection);
        cardBody.appendChild(ctaSection);
        card.appendChild(img);
        card.appendChild(cardBody);

        // Insert the card before the first child of the search results container
        searchResultsContainer.appendChild(card);
            });
}


});
$('.item').on('click', function() {
    // Get the ID of the clicked item
    var itemId = $(this).attr('id');

    // Perform actions based on the clicked item ID
    switch(itemId) {
        case 'btp':
                // Handle click event for electronics item
                console.log('btp clicked');
                // Send AJAX request to server
                $.ajax({
                    url: '/search_mention',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ search_query: 'batiments et travaux publics' }), // Set the search query
                    success: function(response) {
                        // Process the response
                        console.log(response);
                        $('.search-results').html('');
                        renderSearchResultsMention(response);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                    }
                });
                break;
        case 'geologie':
                // Handle click event for electronics item
                console.log('geologie clicked');
                // Send AJAX request to server
                $.ajax({
                    url: '/search_mention',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ search_query: 'genie geologique' }), // Set the search query
                    success: function(response) {
                        // Process the response
                        console.log(response);
                        $('.search-results').html('');
                        renderSearchResultsMention(response);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                    }
                });
                break;
        case 'mine':
                // Handle click event for electronics item
                console.log('mine clicked');
                // Send AJAX request to server
                $.ajax({
                    url: '/search_mention',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ search_query: 'ingenierie miniere' }), // Set the search query
                    success: function(response) {
                        // Process the response
                        console.log(response);
                        $('.search-results').html('');
                        renderSearchResultsMention(response);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                    }
                });
                break;
        case 'electronics':
                // Handle click event for electronics item
                console.log('btp clicked');
                // Send AJAX request to server
                $.ajax({
                    url: '/search_mention',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ search_query: 'electronique' }), // Set the search query
                    success: function(response) {
                        // Process the response
                        console.log(response);
                        $('.search-results').html('');
                        renderSearchResultsMention(response);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                    }
                });
                break;
        case 'petroliere':
                // Handle click event for electronics item
                console.log('petroliere clicked');
                // Send AJAX request to server
                $.ajax({
                    url: '/search_mention',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ search_query: 'ingenierie petroliere' }), // Set the search query
                    success: function(response) {
                        // Process the response
                        console.log(response);
                        $('.search-results').html('');
                        renderSearchResultsMention(response);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                    }
                });
                break;
        case 'hydraulique':
                // Handle click event for electronics item
                console.log('hydraulique clicked');
                // Send AJAX request to server
                $.ajax({
                    url: '/search_mention',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ search_query: 'hydraulique' }), // Set the search query
                    success: function(response) {
                        // Process the response
                        console.log(response);
                        $('.search-results').html('');
                        renderSearchResultsMention(response);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                    }
                });
                break;
        case 'igat':
                // Handle click event for electronics item
                console.log('igat item clicked');
                // Send AJAX request to server
                $.ajax({
                    url: '/search_mention',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ search_query: 'information geographique et amenagement du territoire' }), // Set the search query
                    success: function(response) {
                        // Process the response
                        console.log(response);
                        $('.search-results').html('');
                        renderSearchResultsMention(response);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                    }
                });
                break;
        case 'tco':
                // Handle click event for electronics item
                console.log('tco item clicked');
                // Send AJAX request to server
                $.ajax({
                    url: '/search_mention',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ search_query: 'telecommunication' }), // Set the search query
                    success: function(response) {
                        // Process the response
                        console.log(response);
                        $('.search-results').html('');
                        renderSearchResultsMention(response);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                    }
                });
                break;

        case 'ge':
                // Handle click event for electronics item
                console.log('ge item clicked');
                // Send AJAX request to server
                $.ajax({
                    url: '/search_mention',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ search_query: 'genie electrique' }), // Set the search query
                    success: function(response) {
                        // Process the response
                        console.log(response);
                        $('.search-results').html('');
                        renderSearchResultsMention(response);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                    }
                });
                break;
        case 'mto':
            // Handle click event for electronics item
            console.log('meteorologie item clicked');
            // Send AJAX request to server
            $.ajax({
                url: '/search_mention',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ search_query: 'meteorologie' }), // Set the search query
                success: function(response) {
                    // Process the response
                    console.log(response);
                    $('.search-results').html('');
                    renderSearchResultsMention(response);
                },
                error: function(xhr, status, error) {
                    console.error('Error:', error);
                }
            });
            break;
        case 'gmi':
            // Handle click event for electronics item
            console.log('gmi item clicked');
            // Send AJAX request to server
            $.ajax({
                url: '/search_mention',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ search_query: 'genie mecanique et industriel' }), // Set the search query
                success: function(response) {
                    // Process the response
                    console.log(response);
                    $('.search-results').html('');
                    renderSearchResultsMention(response);
                },
                error: function(xhr, status, error) {
                    console.error('Error:', error);
                }
            });
            break;
        case 'gpci':
            // Handle click event for electronics item
            console.log('mto item clicked');
            // Send AJAX request to server
            $.ajax({
                url: '/search_mention',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ search_query: 'genie des procedes chimiques et industriels' }), // Set the search query
                success: function(response) {
                    // Process the response
                    console.log(response);
                    $('.search-results').html('');
                    renderSearchResultsMention(response);
                },
                error: function(xhr, status, error) {
                    console.error('Error:', error);
                }
            });
            break;
        case 'sim':
            // Handle click event for electronics item
            console.log('sim item clicked');
            // Send AJAX request to server
            $.ajax({
                url: '/search_mention',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ search_query: 'science et ingenierie des materiaux' }), // Set the search query
                success: function(response) {
                    // Process the response
                    console.log(response);
                    $('.search-results').html('');
                    renderSearchResultsMention(response);
                },
                error: function(xhr, status, error) {
                    console.error('Error:', error);
                }
            });
            break;
        case 'urbanisme':
                // Handle click event for electronics item
                console.log('btp clicked');
                // Send AJAX request to server
                $.ajax({
                    url: '/search_mention',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ search_query: 'urbanisme - architecture et genie civil' }), // Set the search query
                    success: function(response) {
                        // Process the response
                        console.log(response);
                        $('.search-results').html('');
                        renderSearchResultsMention(response);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                    }
                });
                break;
    }
});
function renderSearchResultsMention(data) {
    const searchResultsContainer = document.querySelector('.search-results');
    const searchResultsContainerAll = document.querySelector('.search-results-all');

    // Create and append label for search results
    const searchResultsLabel = document.createElement('h2');
    searchResultsLabel.textContent = "Résultat(s) de la recherche";
    searchResultsLabel.style.fontFamily = 'Montserrat'; // Set Montserrat font family
    searchResultsLabel.style.fontWeight = 'normal'; // Set normal font weight
    searchResultsContainer.appendChild(searchResultsLabel);
    data.forEach(result => {
        // Create elements for displaying search results
        const card = document.createElement('div');
        card.className = 'card bg-light-subtle mb-3';

        const img = document.createElement('img');
        img.src = `data:image/png;base64,${result.cover_image_base64}`;
        img.className = 'card-img';
        img.alt = '...';

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';

        const textSection = document.createElement('div');
        textSection.className = 'text-section';

        const title = document.createElement('h6');
        title.className = 'card-title';
        title.style = 'overflow-wrap: break-word; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;';
        title.innerText = result.title;

        const author = document.createElement('h6');
        author.className = 'card-title';
        author.innerText = result.author;

        const mention = document.createElement('p');
        mention.className = 'card-text';
        mention.style = 'overflow-wrap: break-word; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;';
        mention.innerText = result.mention;

        const theme = document.createElement('p');
        theme.className = 'card-text';
        theme.style = 'overflow-wrap: break-word; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;';
        theme.innerText = result.theme;

        const date = document.createElement('p');
        date.className = 'card-text';
        date.innerText = result.date;

        const ctaSection = document.createElement('div');
        ctaSection.className = 'cta-section';

        const downloadLink = document.createElement('a');
        downloadLink.href = result.download_link;
        downloadLink.className = 'btn btn-dark';
        downloadLink.innerText = 'Download';

        // Append elements
        ctaSection.appendChild(downloadLink);
        textSection.appendChild(title);
        textSection.appendChild(author);
        textSection.appendChild(mention);
        textSection.appendChild(theme);
        textSection.appendChild(date);
        cardBody.appendChild(textSection);
        cardBody.appendChild(ctaSection);
        card.appendChild(img);
        card.appendChild(cardBody);

        searchResultsContainer.appendChild(card);


    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Get the login button element
    var loginButton = document.getElementById('LoginButton');

    // Add click event listener to the button
    if (loginButton) {
        loginButton.addEventListener('click', function() {
            // Redirect to the /login page
            window.location.href = '/login';
        });
    }
});

// JavaScript function to handle theme click
$('.book-type').click(function() {
    var search_query = $(this).text().trim(); // Get the theme text
    $.ajax({
        url: '/search_theme',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ search_query: search_query }),
        success: function(response) {
            // Clear previous search results
            $('#search-results-theme').empty();
            // Loop through search results and generate HTML
            console.log(response)
            response.forEach(function(book) {
                var html = `<div class="card bg-light-subtle mt-4">
                                <img src="data:image/png;base64,${book.cover_image_base64}" class="card-img-top" alt="Book Cover" style="width: 140px; min-width: 130px;height: 180px;">
                                <div class="card-body">
                                  <div class="text-section">
                                    <h5 class="card-title">${book.title}</h5>
                                    <h6 class="card-title">${book.author}</h6>
                                    <p class="card-text">${book.mention}</p>
                                    <p class="card-text">${book.date}</p>
                                  </div>
                                  <div class="cta-section d-flex justify-content-end">
                                    <a href="${book.download_link}" class="btn btn-light">Download</a>
                                  </div>
                                </div>
                            </div>`;
                $('#search-results-theme').append(html); // Append HTML to search results div
            });
        }
    });
});


window.addEventListener('resize', adjustTitleWidth);

function adjustTitleWidth() {
  var cardWidth = document.getElementById('card-body').clientWidth;
  var title = document.getElementById('title');
  title.style.maxWidth = (cardWidth - 20) + 'px'; // Adjust 20 as needed for padding, margins, etc.
}


