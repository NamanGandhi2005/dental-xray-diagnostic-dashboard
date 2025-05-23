# Stage 1: Build the React app
FROM node:18-alpine as builder
# node:18-alpine is a lightweight Node.js image

WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./
# COPY yarn.lock ./ # If using Yarn

# Install dependencies
RUN npm install
# RUN yarn install # If using Yarn

# Copy the rest of the application code
COPY . .

# Environment variable for the API URL during build time.
# This will be the URL of the backend *inside the Docker network*.
# It will be proxied by Nginx in the final stage.
# For now, we'll use /api/ which Nginx will proxy.
ARG VITE_API_BASE_URL=/api/
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build the production version of the app
RUN npm run build

# Stage 2: Serve the static files with Nginx
FROM nginx:stable-alpine

# Copy the built static files from the builder stage to Nginx's web server directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy a custom Nginx configuration file (we'll create this next)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (Nginx default port)
EXPOSE 80

# Command to start Nginx
CMD ["nginx", "-g", "daemon off;"]