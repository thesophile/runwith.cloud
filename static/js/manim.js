var editor = CodeMirror.fromTextArea(document.getElementById('code'), {
            mode: 'python',
            lineNumbers: true,
            tabSize: 4,
            // value: 'from manim import*',
            theme: 'dracula',
            extraKeys: {
            "Ctrl-Space": "autocomplete"  // Bind autocomplete to Ctrl-Space
            }
        });
        
        // editor.setValue(previous_code);
        // editor.setOption('theme', 'dracula');
   


    var toggle_button = document.getElementsByClassName('theme-toggle')[0];
    toggle_button.addEventListener('change', function() {
    var Box = toggle_button.getElementsByTagName('input')[0];    
    if (Box.checked) {
        editor.setOption("theme", "eclipse");  // Dark mode
    } else {
        editor.setOption("theme", "dracula");  // Light mode
    }
    });

    
    
        // Get the modal
        var modal = document.getElementById("save-modal");
    
        // Get the button that opens the modal
        var savenewBtn = document.getElementById("save-new-btn");
    
        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];
        var openDropdown = document.getElementById("saved-codes");   
        var saveBtn = document.getElementById("save-btn");
        var SaveCurrentForm = document.getElementById("save-current-form");


        const openButton = document.getElementById('open-button');
        const openList = document.getElementById('open-list');
        // const noOptionsMessage = document.getElementById('no-options-message');

        const examplesButton = document.getElementById('examples-button');
        const examplesList = document.getElementById('examples-list');

        savenewBtn.onclick = function() {
            if (isAuthenticated){
                modal.style.display = "block";                         
            }
            else{
                alert("You have to Log in to do that");
            }
        }
    
        span.onclick = function() {
            modal.style.display = "none";
        }
    
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }
    
        document.getElementById("save-new-form").onsubmit = function() {
            var name = document.getElementById("name").value.trim();
            if (name === "") {
                alert("Please enter a name for the code.");
                return false; // Prevent form submission
            }
            else{
                console.log(`New code name: ${name}`);
                setCodeName(name);
                editor.setValue('');
            }
        }

        document.getElementById('save-new-form').addEventListener('submit', function(event) {
            var visible_code = document.getElementById('code').value;
            // console.log(`visible_code: ${visible_code}`);
            var hidden_code= document.getElementById('hidden_code_new');
            hidden_code.value = visible_code;
        });

        // openDropdown.onclick = function(event) {
        //     if(!isAuthenticated){
        //         event.preventDefault();
        //         alert('You will have to Log in to do that');
        //     }else {
        //         var options = openDropdown.getElementsByTagName("option");
        //         if (options.length === 1) { // Check if only the default option is present
        //             event.preventDefault();
        //             alert("You have no saved projects. Create a new project first.");
        //         } else {
        //             console.log("Options are present.");
        //         }
        //     }
        // }

 

        // Toggle dropdown list visibility
        openButton.onclick = function(event) {
            if(!isAuthenticated){
                event.preventDefault();
                alert('You will have to Log in to do that');
                return;
            }
            
            const options = openList.querySelectorAll('.dropdown-item');
            console.log(options.length);
            if (options.length === 0) {
                alert("You have no saved projects. Create a new project first.");
                return;
            } else {
                openList.style.display = openList.style.display === "none" ? "block" : "none";
            }

            
        };

        examplesButton.onclick = function(event) {
            examplesList.style.display = examplesList.style.display === "none" ? "block" : "none";
        };

        // Handle clicking an option
        openList.addEventListener('click', function(event) {
            const item = event.target.closest('.dropdown-item');
            if(!item) return;

            const codeId = item.dataset.id;
            console.log(`CodeId for selected dropdown: ${codeId}`);

            // You can call your function to open code here
            opencode(codeId);
            

            openList.style.display = "none"; // close the dropdown
        });

        // Handle clicking an option
        examplesList.addEventListener('click', function(event) {
            const item = event.target.closest('.dropdown-item');
            if(!item) return;

            const selectedExample = item.dataset.name;
            console.log(`Selected Example : ${selectedExample}`);

            if (examples[selectedExample]) {
                editor.setValue(examples[selectedExample])
            }

            examplesList.style.display = "none"; // close the dropdown
        });


        //  close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!openButton.contains(event.target) && !openList.contains(event.target)) {
                openList.style.display = "none";
            }
        });

        document.addEventListener('click', function(event) {
            if (!examplesButton.contains(event.target) && !examplesList.contains(event.target)) {
                examplesList.style.display = "none";
            }
        });



        // //Open Codes
        // openDropdown.onchange = function() {
        //     var codeId = this.value;
        //     console.log(`CodeId for seleted dropdown: ${codeId}`)

            
        //}

        // Save Button
        saveBtn.onclick = async function (event) {
            event.preventDefault();

            if (!isAuthenticated) {
                alert("You have to log in to do that");
                return;
            }

            // Get code name first
            try {
                const response = await fetch('get_code_name/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const data = await response.json();
                const codeName = data.result;
                console.log('Code Name:', codeName);

                if (!codeName) {
                    alert('Create new project first');
                    console.log('getCodeName returned Null');
                    return;
                }

                // Get code from CodeMirror editor
                const inputCode = editor.getValue();
                console.log('Input code:', inputCode);

                if (!inputCode) {
                    alert('Input cannot be empty.');
                    return;
                }

                // Save the code
                const saveResponse = await fetch('save_current_code/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                    body: JSON.stringify({
                        code_text: inputCode,
                        code_name: codeName,
                        form_type: 'save_current'
                    }),
                });

                if (saveResponse.ok) {
                    alert('Code saved successfully!');
                } else {
                    const errorText = await saveResponse.text();
                    console.log('Error response:', errorText);
                    alert('Failed to save code.');
                }

            } catch (error) {
                console.error('Error:', error);
                alert('An unexpected error occurred while saving.');
            }
        };
        


   


    

    