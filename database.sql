-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Pairs
CREATE TABLE pairs (
    id SERIAL PRIMARY KEY,
    user1_id INTEGER REFERENCES users(id),
    user2_id INTEGER REFERENCES users(id),
    invite_code VARCHAR(10) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_pair UNIQUE(user1_id, user2_id)
);

-- Date Ideas
CREATE TABLE ideas (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) DEFAULT 'general',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Date Proposals
CREATE TABLE date_proposals (
    id SERIAL PRIMARY KEY,
    pair_id INTEGER REFERENCES pairs(id),
    idea_id INTEGER REFERENCES ideas(id),
    proposer_id INTEGER REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, rejected, completed
    scheduled_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index creation for performance optimization
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_pairs_users ON pairs(user1_id, user2_id);
CREATE INDEX idx_proposals_pair ON date_proposals(pair_id);
CREATE INDEX idx_proposals_status ON date_proposals(status);

-- Base date ideas
INSERT INTO ideas (title, description, category) VALUES
('Пикник в парке', 'Устройте романтический пикник на природе с любимыми закусками', 'романтика'),
('Домашний кинотеатр', 'Посмотрите фильм дома с попкорном и объятиями', 'дом'),
('Прогулка по городу', 'Исследуйте новые места в вашем городе', 'активность'),
('Готовим вместе', 'Приготовьте ужин вместе, попробуйте новый рецепт', 'дом'),
('Поход в музей', 'Посетите местный музей или выставку', 'культура'),
('Кафе или ресторан', 'Сходите в новое место, которое давно хотели попробовать', 'ресторан'),
('Настольные игры', 'Вечер настольных игр дома с чаем или вином', 'дом'),
('Фотосессия', 'Устройте импровизированную фотосессию в красивом месте', 'творчество'),
('Spa дома', 'Расслабляющий вечер с масками, массажем и свечами', 'релакс'),
('Танцы', 'Потанцуйте дома под любимую музыку', 'активность'),
('Книжный магазин', 'Выберите друг другу книги в книжном магазине', 'культура'),
('Завтрак в постель', 'Приготовьте друг другу завтрак в постель', 'романтика'),
('Прогулка на закате', 'Прогуляйтесь вместе во время заката', 'романтика'),
('Игра в боулинг', 'Сходите в боулинг и устройте соревнование', 'активность'),
('Квест-комната', 'Решайте головоломки и загадки вместе', 'активность');