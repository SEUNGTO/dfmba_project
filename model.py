import torch
import torch.nn as nn

class VisionModel(nn.Module):
    def __init__(self, latent_dim=32):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, 4, stride=2, padding=1),  
            nn.ReLU(),
            nn.Conv2d(32, 64, 4, stride=2, padding=1), 
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(64*8*8, latent_dim*2)  # mean, logvar
        )

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 64*8*8),
            nn.ReLU(),
            nn.Unflatten(1, (64, 8, 8)),
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(32, 3, 4, stride=2, padding=1),
            nn.Sigmoid()
        )

    def encode(self, x):
        mu_logvar = self.encoder(x)
        mu, logvar = mu_logvar.chunk(2, dim=-1)
        return mu, logvar

    def decode(self, z):
        return self.decoder(z)


class MemoryModel(nn.Module):
    def __init__(self, latent_dim=32, action_dim=6, hidden_dim=256):
        super().__init__()
        self.rnn = nn.GRU(latent_dim + action_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, latent_dim)

    def forward(self, z, a, h=None):
        # z: (B, T, latent_dim), a: (B, T, action_dim)
        x = torch.cat([z, a], dim=-1)
        out, h_next = self.rnn(x, h)
        z_next = self.fc(out)
        return z_next, h_next


class Controller(nn.Module):
    def __init__(self, latent_dim=32, hidden_dim=256, action_dim=6):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(latent_dim + hidden_dim, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim),
            nn.Tanh()  # action 범위 제한
        )

    def forward(self, z, h):
        x = torch.cat([z, h], dim=-1)
        return self.fc(x)
    
    
