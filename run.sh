docker run --rm -it -p 1313:1313 \
  -v "$PWD":/src -w /src \
  klakegg/hugo:ext \
  server -D --bind 0.0.0.0 --baseURL http://localhost:1313/ \
  --forceSyncStatic --ignoreCache --disableFastRender --cleanDestinationDir
