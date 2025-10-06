//         saveBtn.onclick = function (event) {

//             // Check if there is a code_name, else we can't save
//             async function getCodeName() {
//                 try {
//                     const response = await fetch('get_code_name/', {
//                         method: 'POST',
//                         headers: {
//                             'Content-Type': 'application/json',
//                             'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
//                         },
//                     });

//                     if (!response.ok) {
//                         throw new Error(`HTTP error! Status: ${response.status}`);
//                     }

//                     const data = await response.json();
//                     return data.result;
//                 } catch (error) {
//                     console.error('Error:', error);
//                     return null; // Return null or handle the error as required
//                 }
//             }

//             // get code name
//             (async () => {
//                 const result = await getCodeName();
//                 console.log('Code Name:', result);
//             })();
                
//             // result = getCodeName(); //check if current_code_present   
//             // console.log(`result: ${result}`)        
          
//             if (!isAuthenticated) {
//                 event.preventDefault();
//                 alert("You have to log in to do that");
//             } else if (!result) {
//                 event.preventDefault();
//                 alert('Create new project first');
//                 console.log(`result - getCodeName returned Null`);
//             } else {

//                 // const inputCode = document.getElementById('code').value ;
//                 const inputCode = editor.getValue(); // Get code from CodeMirror editor instead of textarea
//                 console.log(`inputCode: ${inputCode}`);

//                 if (!inputCode) {
//                     alert('Input cannot be empty.');
//                     return;
//                 }

//                 // Wrap the fetch in an IIFE to allow async/await
//                 (async function () {
//                     try {
//                         const response = await fetch('save_current_code/', {
//                             method: 'POST',
//                             headers: {
//                                 'Content-Type': 'application/json',
//                             },
//                             body: JSON.stringify({ code_text: inputCode }),
//                         });

//                         if (response.ok) {
//                             alert('Value saved successfully!');
//                         } else {
//                             alert('Failed to save value.');
//                             console.log('Error response:', await response.text());
//                         }
//                     } catch (error) {
//                         console.error('Error saving value:', error);
//                         alert('An unexpected error occurred while saving.');
//                     }
//                 })();
//             }
// };

// OLD saveButton script
// saveBtn.onclick = function (event) {
//             if (!isAuthenticated) {
//                 event.preventDefault();
//                 alert("You have to log in to do that");
//             } else if (!current_code_present) {
//                 event.preventDefault();
//                 alert('Create new project first');
//                 console.log(`current_code_present: ${current_code_present}`);
//             } else {
//                 var visible_code = document.getElementById('code').value;
//                 var hidden_code= document.getElementById('hidden_code_current');
//                 hidden_code.value = visible_code;
//                 console.log(`hidden_code_value: ${hidden_code.value}`);
//                 SaveCurrentForm.submit();
//             }
// }
