document.addEventListener('DOMContentLoaded', function () {
    // Add event listeners to all posts and following buttons
    document.querySelector('#all').addEventListener('click', () => load_feed('all'));
    document.querySelector('#following').addEventListener('click', () => load_feed('following'));
    load_feed('all')

});

function load_feed(feed) {
    // set all other sections to hidden
    document.querySelector('#posts-view').style.display = 'block';
    document.querySelector('#profile-view').style.display = 'none';
    document.querySelector('#follow-view').style.display = 'none';
    document.querySelector('#post-view').style.display = 'none';

    // clear out the posts section 
    document.querySelector('#posts-section').innerHTML = '';

    // make an ajax request to get the posts
    // if feed is all make it ''
    if (feed == 'all') {
        feed = ''
    }
    fetch('posts/' + feed, {
            method: 'GET',
        })
        .then(response => response.json())
        .then(result => {
            // Print result
            console.log(result);

            // present the posts
            // for each post, present the post
            for (let i = 0; i < result.length; i++) {
                // get the post
                let post = result[i];
                // create a new post element
                let postElement = document.createElement('div');
                postElement.className = 'post';
                // will add content, author, time, and likes 
                postElement.innerHTML = `
                    <div class="post-content">
                        <div class="post-header">
                            <div class="post-author">
                            <a class="link-primary post-author-link" href="javascript:load_profile('${post.author}')">${post.author}</a>
                            </div>
                            <div class="post-time">

                                ${new Date(post.updated_at).toLocaleString()}
                            </div>
                        </div>
                        <div class="post-body">
                            <p>${post.content}</p>
                        </div>
                        <div class="post-footer">
                            <div class="post-likes">
                                <a>${post.likes} Likes</a>
                            </div>
                            <hr>
            </div>
        `;
                // add event listener to the profile link to call load_profile

                // add the post element to the posts section
                document.querySelector('#posts-section').appendChild(postElement);
                // add event listeners to the buttons
                // document.querySelector(`#like-button-${post.id}`).addEventListener('click', () => like_post(post.id));
            }
        });


}

function load_profile(profile) {
    // pass for now
    alert(profile);
    document.querySelector('#posts-view').style.display = 'none';
    document.querySelector('#profile-view').style.display = 'block';
    document.querySelector('#follow-view').style.display = 'none';
    document.querySelector('#post-view').style.display = 'none';

    // get the profile data from the server

}