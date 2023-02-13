document.addEventListener('DOMContentLoaded', function() {

    if (document.getElementById("btnfollow")) {
        document.querySelector("#btnfollow").addEventListener("click", function(event){
            fetch(`/follow/${this.dataset.id}`)
                .then(response => response.json())
                .then(data => {
                    document.querySelector('#numfollowers').innerHTML = data.total_followers;
                    if (data.result == "follow") {
                        this.innerHTML = "Followed";
                        this.className = "btn btn-primary";
                    } else {
                        this.innerHTML = "Follow";
                        this.className = "btn btn-outline-primary";
                    }
                });
            })
        }


    //edit 
    edit = document.querySelectorAll(".edit");
    edit.forEach((element) => {
         element.addEventListener('click',() => {
             edit_handeler(element);
             console.log('button click!')
        })
    })

    //like
    like = document.querySelectorAll(".likedpost")
    like.forEach((element) => {
            like_handeler(element);
        })

});


function edit_post(id, post) {
    form = new FormData();
    form.append("id", id);
    form.append("post", post.trim());

    fetch("/editpost", {
        method:"POST", 
        body: form,
    })
    .then((res) =>{
        document.querySelector(`#post-content-${id}`).textContent = post;
        document.querySelector(`#post-content-${id}`).style.display = "block";
        document.querySelector(`#post-edit-${id}`).style.display = "none";
        document.querySelector(`#post-edit-${id}`).value = post.trim();
    })
}


function edit_handeler(element) {
    id = element.getAttribute("data-id");
    edit_btn = document.querySelector(`#edit-btn-${id}`);
    if (edit_btn.textContent == "Edit") {
      document.querySelector(`#post-content-${id}`).style.display = "none";
      document.querySelector(`#post-edit-${id}`).style.display = "block";
      edit_btn.textContent = "Save";
      edit_btn.setAttribute("class", "text-success edit");
    } else if (edit_btn.textContent == "Save") {
      edit_post(id, document.querySelector(`#post-edit-${id}`).value);
  
      edit_btn.textContent = "Edit";
      edit_btn.setAttribute("class", "text-primary edit");
    }
  }


  function like_handeler(element) {
    element.addEventListener("click", ()=>{
        id = element.getAttribute("data-id");
        console.log(id);
        liked = element.getAttribute("data-liked");
        like_or_liked = document.querySelector(`#post-like-${id}`);
        console.log(like_or_liked);
        count = document.querySelector(`#post-count-${id}`);

        form = new FormData();
        form.append("id", id);
        form.append("liked", liked);

        fetch("/like", {
            method:"POST",
            body: form,
        })
        .then((res) => res.json())
        .then((res) => {
            if (res.status == 201) {
                if (res.liked === 'yes') {
                    like_or_liked.textContent = "Liked";
                    element.setAttribute("data-liked", "yes");
                } else {
                    like_or_liked.textContent = "Like";
                    element.setAttribute("data-liked", "no");
                }
                count.textContent = res.like_count;
            }
        })
    })
}