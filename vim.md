Vim things

mostly sourced from here: 
https://bitbucket.org/sjl/dotfiles/src/tip/vim/vimrc?fileviewer=file-view-default

These make j and k move by line on the screen, rather than line in the file. 
It's for when there are wrapped lines.
```
noremap j gj
noremap k gk
noremap gj j
noremap gk k
```

Keep search matches in the middle of the window.

```
nnoremap n nzzzv
nnoremap N Nzzzv
```

Same when jumping around
```
nnoremap g; g;zz
nnoremap g, g,zz
nnoremap <c-o> <c-o>zz
```

More intuitive characters for these functions. 
They're like 'strong' versions of h and l. 

```
noremap H ^
noremap L $
```