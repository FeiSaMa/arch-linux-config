if vim.g.vscode then
  vim.g.mapleader = " "
  vim.g.maplocalleader = " "
  vim.keymap.set({ "n", "x" }, "<Space>", "<Nop>", { silent = true })
  vim.keymap.set("n", "<C-n>", ":nohlsearch<CR>", { silent = true })
  vim.keymap.set("n", "<leader>d", "dd", { silent = true })
  return
end

-- bootstrap lazy.nvim, LazyVim and your plugins
require("config.lazy")
