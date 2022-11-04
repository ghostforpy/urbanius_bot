
export PGHOST="localhost"
export PGPORT="5432"
export PGUSER="postgres"
export PGPASSWORD=""
export PGDATABASE=""
backup_filename=$1

message_info "Dropping the database..."
dropdb "${PGDATABASE}"

message_info "Creating a new database..."
createdb --owner="${PGUSER}"

message_info "Applying the backup to the new database..."
gunzip -c "${backup_filename}" | psql "${PGDATABASE}"

message_success "The '${PGDATABASE}' database has been restored from the '${backup_filename}' backup."