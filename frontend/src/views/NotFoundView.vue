<template>
  <div class="not-found-container">
    <div class="content">
      <div class="icon">😕</div>
      <h1>404 – Page Not Found</h1>
      <p>Sorry, the page you're looking for doesn't exist.</p>
      <router-link to="/" class="home-link">Go back to Home</router-link>
    </div>
  </div>
</template>

<script lang="ts" setup>
</script>

<style lang="scss" scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  color: #ffffff;
  text-align: center;
}

.content {
  max-width: 500px;
}

.icon {
  font-size: 5rem;
  margin-bottom: 1rem;
}

h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

p {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  color: #cccccc;
}

.home-link {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  background-color: #2d3748; // Dark gray-blue
  color: #ffffff;
  text-decoration: none;
  border-radius: 0.5rem;
  font-weight: 500;
  box-shadow: 0 0 0 2px transparent;
  transition: background-color 0.3s, box-shadow 0.2s, transform 0.2s;

  &:hover {
    background-color: #4a5568; // Slightly lighter on hover
    transform: translateY(-1px);
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px #63b3ed; // Blue focus ring
  }

  &:active {
    background-color: #2c5282; // Slightly stronger on click
    transform: translateY(0);
  }
}
</style>
