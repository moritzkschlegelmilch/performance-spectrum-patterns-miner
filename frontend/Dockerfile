# sudo docker build --no-cache -t vue-frontend-test .
# Use the official Node.js image to build the frontend
FROM node:18-alpine as build

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json
COPY package*.json ./
COPY tsconfig.json ./
COPY tsconfig.app.json ./
COPY tsconfig.node.json ./

# Install frontend dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .
RUN mv .example.env .env

# Build the frontend
RUN npm run build --host
# RUN npm run build

# Expose the port for the frontend
# EXPOSE 5173

# Use Nginx to serve the static files
FROM nginx:alpine

# Copy the build output to NGINX's default HTML directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for the container
EXPOSE 80

# Start NGINX when the container runs
CMD ["nginx", "-g", "daemon off;"]
