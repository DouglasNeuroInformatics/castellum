#!/bin/sh

sed -i 's/\(load.*\)bootstrap4/\1django_bootstrap5/g' `git grep -l bootstrap4`
git commit -a -m "auto-adapt bootstrap template library"

sed -i 's/var(--/var(--bs-/g' `git ls-files castellum | grep 'css'`
git commit -a -m "auto-adapt CSS variables"

sed -i 's/data-\(toggle\|dismiss\)/data-bs-\1/g' `git grep -l 'data-' castellum`
sed -i 's/\(data-bs.*\)data-target/\1data-bs-target/g' `git grep -l 'data-' castellum`
git commit -a -m "auto-adapt data-* hooks"

sed -i 's/mr-/me-/g' `git grep -l 'mr-' castellum`
sed -i 's/ml-/ms-/g' `git grep -l 'ml-' castellum`
sed -i 's/text-right/text-end/g' `git grep -l 'text-right' castellum`
sed -i 's/text-left/text-start/g' `git grep -l 'text-left' castellum`
sed -i 's/float-right/float-end/g' `git grep -l 'float-right' castellum`
sed -i 's/float-left/float-start/g' `git grep -l 'float-left' castellum`
git commit -a -m "auto-adapt utilities"

sed -i 's/btn-block/d-block w-100/g' `git grep -l 'btn-block' castellum`
git commit -a -m "auto-adapt btn-block"

sed -i 's/form-row/row gx-2/g' `git grep -l 'form-row' castellum`
git commit -a -m "auto-adapt form row"

sed -i 's/form-group/mb-3/g' `git grep -l 'form-group' castellum`
git commit -a -m "auto-adapt form-group"

sed -i 's/form_group_class=.. /layout="inline" /g' `git grep -l 'form_group_class' castellum`
git commit -a -m "auto-adapt form_group_class"

sed -i 's/badge-light/bg-light text-body/g' `git grep -l 'badge-light' castellum`
sed -i 's/badge-warning/bg-warning text-dark/g' `git grep -l 'badge-warning' castellum`
sed -i 's/badge-/bg-/g' `git grep -l 'badge-' castellum`
git commit -a -m "auto-adapt badges"

rm migrate.sh
git commit -a -m "rm migrate script"
