{
  inputs = {
    nixpkgs = {
      url = "github:NixOS/nixpkgs/nixos-24.05";
    };

    flake-utils = {
      url = "github:numtide/flake-utils";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {self, nixpkgs, flake-utils, poetry2nix, ...}@inputs :
  flake-utils.lib.eachDefaultSystem (system: 
  let
    pkgs = import nixpkgs {inherit system;};
    inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
  in
  {
    packages = {
      chipift = mkPoetryApplication {
        projectDir = self;
        python = pkgs.python312;
      };
      default = self.packages.${system}.chipift;
    };
    devShells.default = pkgs.mkShell {
      inputsFrom = [ self.packages.${system}.chipift ];
      packages = with pkgs; [
        yosys
        verilog
      ];
    };

    devShells.poetry = pkgs.mkShell {
      packages = [ pkgs.poetry ];
    };
    apps.${system}.default = {
      type = "app";
      # replace <script> with the name in the [tool.poetry.scripts] section of your pyproject.toml
      program = "${self.packages.chipift}/bin/chipift";
    };
  });
}
