document.addEventListener('DOMContentLoaded', function() {
    const formContainer = document.getElementById('form-container');
    const infoPopup = document.querySelector('.form-popup');
    const containerUpload = document.querySelector('.container_upload');
    let animationTimeout;

    function closeForm() {
        console.log('Closing form');
        formContainer.style.display = 'none';
        document.body.classList.remove('overlay-active');
    }

    function closeInfoPopup() {
        console.log('Closing info popup');
        infoPopup.style.display = 'none';
        document.body.classList.remove('overlay-active');
    }

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

    document.querySelector('.deposit-button').addEventListener('click', function() {
        console.log('Deposit button clicked');
        formContainer.style.display = 'flex';
        infoPopup.style.display = 'none';
        document.body.classList.add('overlay-active');
    });

    document.querySelector('.member-button').addEventListener('click', function() {
        console.log('Member button clicked');
        window.location.href = '/login22';
    });

    document.querySelectorAll('.btn-close').forEach(button => {
        button.addEventListener('click', closeForm);
    });

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

    document.getElementById('exampleInputnumber').addEventListener('input', togglePublishButton);
    document.getElementById('exampleInputSchool').addEventListener('input', togglePublishButton);
    document.getElementById('exampleInputName').addEventListener('input', togglePublishButton);
    document.getElementById('exampleInputEmail').addEventListener('input', togglePublishButton);
    document.getElementById('memoir-files').addEventListener('change', togglePublishButton);
    document.getElementById('correction-attestation').addEventListener('change', togglePublishButton);

    document.querySelector('.edit').addEventListener('click', toggleEdit);

    document.querySelector('.validate').addEventListener('click', async function() {
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
                    closeInfoPopup();
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
                });
        }
    });

    document.querySelector('.form-popup .btn-close').addEventListener('click', closeInfoPopup);
    document.querySelector('.form-container .btn-close').addEventListener('click', closeInfoPopup);
});
