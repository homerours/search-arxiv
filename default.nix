with import <nixpkgs> {}; {

  arxivEnv = stdenv.mkDerivation rec {
    name = "arxiv-env";
    buildInputs = [
      python
      pythonPackages.feedparser
      pythonPackages.argparse
    ];
  };

}
