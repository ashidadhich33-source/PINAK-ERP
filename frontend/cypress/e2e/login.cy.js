describe('Login Flow', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('should display login form', () => {
    cy.get('h2').should('contain', 'Sign in to your account');
    cy.get('input[name="username"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');
    cy.get('button[type="submit"]').should('contain', 'Sign in');
  });

  it('should show validation errors for empty fields', () => {
    cy.get('button[type="submit"]').click();
    
    cy.get('text=Username is required').should('be.visible');
    cy.get('text=Password is required').should('be.visible');
  });

  it('should show validation error for short username', () => {
    cy.get('input[name="username"]').type('ab');
    cy.get('button[type="submit"]').click();
    
    cy.get('text=Username must be at least 3 characters').should('be.visible');
  });

  it('should show validation error for short password', () => {
    cy.get('input[name="password"]').type('123');
    cy.get('button[type="submit"]').click();
    
    cy.get('text=Password must be at least 6 characters').should('be.visible');
  });

  it('should toggle password visibility', () => {
    cy.get('input[name="password"]').should('have.attr', 'type', 'password');
    
    cy.get('button[aria-label="Show password"]').click();
    cy.get('input[name="password"]').should('have.attr', 'type', 'text');
    
    cy.get('button[aria-label="Hide password"]').click();
    cy.get('input[name="password"]').should('have.attr', 'type', 'password');
  });

  it('should submit form with valid credentials', () => {
    // Mock successful login
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 200,
      body: {
        access_token: 'mock-token',
        token_type: 'bearer',
        expires_in: 3600,
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true,
          is_superuser: false,
          roles: []
        }
      }
    }).as('loginRequest');

    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();

    cy.wait('@loginRequest');
    cy.url().should('include', '/dashboard');
  });

  it('should show error for invalid credentials', () => {
    // Mock failed login
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 401,
      body: {
        detail: 'Invalid credentials'
      }
    }).as('loginRequest');

    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('wrongpassword');
    cy.get('button[type="submit"]').click();

    cy.wait('@loginRequest');
    cy.get('text=Invalid credentials').should('be.visible');
  });
});